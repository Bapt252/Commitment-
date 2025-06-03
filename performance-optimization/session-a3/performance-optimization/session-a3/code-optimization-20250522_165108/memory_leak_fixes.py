"""
Session A3 - Common Memory Leak Fixes
"""

import asyncio
import aiohttp
from contextlib import asynccontextmanager
import weakref

# Fix 1: Proper connection management
@asynccontextmanager
async def managed_http_session():
    """Properly managed HTTP session to prevent connection leaks"""
    connector = aiohttp.TCPConnector(
        limit=100,
        limit_per_host=30,
        ttl_dns_cache=300,
        use_dns_cache=True,
        keepalive_timeout=30,
        enable_cleanup_closed=True
    )
    
    session = aiohttp.ClientSession(connector=connector)
    try:
        yield session
    finally:
        await session.close()
        # Ensure connector cleanup
        await connector.close()

# Fix 2: Prevent circular references in callbacks
class EventManager:
    def __init__(self):
        self._callbacks = weakref.WeakSet()  # Use weak references
    
    def register_callback(self, callback):
        self._callbacks.add(callback)
    
    def unregister_callback(self, callback):
        self._callbacks.discard(callback)
    
    async def notify_all(self, event_data):
        # Iterate over a copy to avoid modification during iteration
        callbacks = list(self._callbacks)
        for callback in callbacks:
            try:
                await callback(event_data)
            except Exception as e:
                logging.error(f"Callback error: {e}")

# Fix 3: Proper file handle management
@asynccontextmanager
async def managed_file_processing(file_path: str):
    """Ensure files are properly closed"""
    file_handle = None
    try:
        file_handle = await aiofiles.open(file_path, 'rb')
        yield file_handle
    finally:
        if file_handle:
            await file_handle.close()

# Fix 4: Database connection leak prevention
class DatabaseManager:
    def __init__(self, pool):
        self.pool = pool
        self._active_connections = weakref.WeakSet()
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = await self.pool.acquire()
        self._active_connections.add(conn)
        try:
            yield conn
        finally:
            await self.pool.release(conn)
            self._active_connections.discard(conn)
    
    async def cleanup_connections(self):
        """Force cleanup of any leaked connections"""
        for conn in list(self._active_connections):
            try:
                await self.pool.release(conn)
            except Exception as e:
                logging.error(f"Error cleaning up connection: {e}")

# Fix 5: Task cleanup
class TaskManager:
    def __init__(self):
        self._background_tasks = weakref.WeakSet()
    
    def create_task(self, coro):
        """Create task with automatic cleanup"""
        task = asyncio.create_task(coro)
        self._background_tasks.add(task)
        
        # Add done callback for cleanup
        task.add_done_callback(lambda t: self._background_tasks.discard(t))
        
        return task
    
    async def cleanup_all_tasks(self):
        """Cancel and cleanup all background tasks"""
        tasks = list(self._background_tasks)
        for task in tasks:
            if not task.done():
                task.cancel()
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
