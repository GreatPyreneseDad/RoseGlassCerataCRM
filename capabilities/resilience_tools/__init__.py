"""
CERATA Resilience Tools
Metabolized from litl/backoff and fabfuel/circuitbreaker

Provides retry logic, circuit breakers, and rate limiting for robust lead hunting.

Usage:
    from capabilities.resilience_tools import on_exception, expo, circuit_breaker

    @on_exception(expo, Exception, max_tries=3)
    @circuit_breaker(failure_threshold=5)
    async def hunt_leads(url):
        # Hunting logic with automatic retry and circuit breaking
        ...
"""

import logging
from typing import Optional, Callable, Any
from functools import wraps
import asyncio
import time

logger = logging.getLogger(__name__)

# Try to import backoff library
try:
    import backoff
    from backoff import expo, fibo, constant
    BACKOFF_AVAILABLE = True
except ImportError:
    logger.warning("backoff library not available - install with: pip install backoff")
    BACKOFF_AVAILABLE = False

    # Fallback implementations
    def expo(*args, **kwargs):
        """Fallback exponential backoff"""
        return lambda n: min(2 ** n, 60)  # Max 60 seconds

    def fibo(*args, **kwargs):
        """Fallback fibonacci backoff"""
        def fib(n):
            if n <= 1:
                return n
            a, b = 0, 1
            for _ in range(n):
                a, b = b, a + b
            return min(a, 60)
        return fib

    def constant(interval=1):
        """Fallback constant backoff"""
        return lambda n: interval


# Simplified circuit breaker implementation (fallback)
class CircuitState:
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance.

    Prevents cascading failures by stopping requests to failing services.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker: HALF_OPEN (testing recovery)")
            else:
                raise Exception(f"Circuit breaker OPEN - service unavailable")

        try:
            result = func(*args, **kwargs)

            # Success - reset if in half-open
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info("Circuit breaker: CLOSED (recovered)")

            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.error(f"Circuit breaker: OPEN after {self.failure_count} failures")

            raise e


def on_exception(
    wait_gen: Callable = expo,
    exception: type = Exception,
    max_tries: int = 3,
    max_time: Optional[int] = None
):
    """
    Retry decorator with exponential backoff.

    Args:
        wait_gen: Wait time generator (expo, fibo, constant)
        exception: Exception type to catch and retry
        max_tries: Maximum retry attempts
        max_time: Maximum total time in seconds

    Example:
        @on_exception(expo, requests.RequestException, max_tries=5)
        def fetch_data(url):
            return requests.get(url)
    """
    if BACKOFF_AVAILABLE:
        return backoff.on_exception(
            wait_gen,
            exception,
            max_tries=max_tries,
            max_time=max_time
        )
    else:
        # Fallback implementation
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                wait = wait_gen()
                for attempt in range(1, max_tries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exception as e:
                        if attempt == max_tries:
                            raise e
                        wait_time = wait(attempt - 1)
                        logger.warning(
                            f"Attempt {attempt}/{max_tries} failed: {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        time.sleep(wait_time)
            return wrapper
        return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type = Exception
):
    """
    Circuit breaker decorator.

    Args:
        failure_threshold: Failures before opening circuit
        recovery_timeout: Seconds before retry
        expected_exception: Exception to catch

    Example:
        @circuit_breaker(failure_threshold=3, recovery_timeout=30)
        def call_api(endpoint):
            return requests.get(endpoint)
    """
    breaker = CircuitBreaker(failure_threshold, recovery_timeout, expected_exception)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


# Rate limiting with token bucket
class TokenBucket:
    """
    Token bucket rate limiter.

    Prevents overwhelming services with too many requests.
    """

    def __init__(self, rate: float, capacity: int):
        """
        Initialize token bucket.

        Args:
            rate: Tokens added per second
            capacity: Maximum tokens
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens.

        Returns:
            True if tokens available, False otherwise
        """
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )
        self.last_update = now

    async def wait_for_token(self, tokens: int = 1):
        """Async wait until tokens available"""
        while not self.consume(tokens):
            await asyncio.sleep(1 / self.rate)


def rate_limit(rate: float, capacity: int):
    """
    Rate limiting decorator using token bucket.

    Args:
        rate: Requests per second allowed
        capacity: Burst capacity

    Example:
        @rate_limit(rate=2.0, capacity=5)  # 2 requests/sec, burst of 5
        def api_call():
            ...
    """
    bucket = TokenBucket(rate, capacity)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await bucket.wait_for_token()
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        return wrapper
    return decorator


# Export all
__all__ = [
    'on_exception',
    'expo',
    'fibo',
    'constant',
    'circuit_breaker',
    'CircuitBreaker',
    'CircuitState',
    'rate_limit',
    'TokenBucket',
]
