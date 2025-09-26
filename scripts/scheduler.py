import schedule
import time
import logging
import traceback
from datetime import datetime
from fetch_data import fetch_and_store
from analytics import CryptoAnalytics

# Configure logging for scheduler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/scheduler_log.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class CryptoDataScheduler:
    def __init__(self):
        self.analytics = CryptoAnalytics()
        self.failed_attempts = 0
        self.max_failures = 5
        self.consecutive_failures = 0
        
    def fetch_data_with_retry(self):
        """Fetch data with retry logic and error handling"""
        try:
            logger.info("Starting scheduled data fetch")
            success = fetch_and_store()
            
            if success:
                self.consecutive_failures = 0
                self.failed_attempts = 0
                logger.info("Data fetch completed successfully")
                
                # Update analytics after successful data fetch
                try:
                    logger.info("Updating analytics")
                    self.analytics.update_all_analytics()
                    logger.info("Analytics update completed")
                except Exception as e:
                    logger.error(f"Analytics update failed: {e}")
                    logger.error(traceback.format_exc())
            else:
                self.handle_failure()
                
        except Exception as e:
            logger.error(f"Unexpected error in data fetch: {e}")
            logger.error(traceback.format_exc())
            self.handle_failure()
    
    def handle_failure(self):
        """Handle failed data fetch attempts"""
        self.consecutive_failures += 1
        self.failed_attempts += 1
        
        logger.warning(f"Data fetch failed. Consecutive failures: {self.consecutive_failures}")
        
        if self.consecutive_failures >= self.max_failures:
            logger.error(f"Too many consecutive failures ({self.consecutive_failures}). "
                        "Consider checking API status or network connectivity.")
            # Reset counter after max failures to avoid infinite blocking
            self.consecutive_failures = 0
    
    def get_status(self):
        """Get current scheduler status"""
        return {
            'total_failures': self.failed_attempts,
            'consecutive_failures': self.consecutive_failures,
            'last_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'next_run': schedule.next_run()
        }
    
    def run_scheduler(self, interval_minutes=5):
        """Run the scheduler with specified interval"""
        logger.info(f"Starting crypto data scheduler with {interval_minutes} minute intervals")
        logger.info(f"Monitoring {len(self.analytics.get_all_symbols())} cryptocurrencies")
        
        # Schedule data fetching
        schedule.every(interval_minutes).minutes.do(self.fetch_data_with_retry)
        
        # Schedule analytics update every hour
        schedule.every().hour.do(self.analytics.update_all_analytics)
        
        # Initial data fetch
        logger.info("Running initial data fetch")
        self.fetch_data_with_retry()
        
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
                # Log status every hour
                if datetime.now().minute == 0:
                    status = self.get_status()
                    logger.info(f"Scheduler status: {status}")
                    
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            logger.error(traceback.format_exc())

def main():
    """Main function to run the scheduler"""
    scheduler = CryptoDataScheduler()
    
    # You can adjust the interval here (1-5 minutes recommended)
    # Be mindful of API rate limits
    scheduler.run_scheduler(interval_minutes=5)

if __name__ == "__main__":
    main()

# Usage examples:
# python scripts/scheduler.py                    # Run with 5-minute intervals
# python scripts/scheduler.py --interval 1      # Run with 1-minute intervals
# python scripts/scheduler.py --interval 10     # Run with 10-minute intervals