from app.daily_runner import run_daily_pipeline


def main(hours: int = 24, top_n: int = 10):
    return run_daily_pipeline(hours=hours, top_n=top_n)


if __name__ == "__main__":
    import sys
    
    hours = 24
    top_n = 10
    
    if len(sys.argv) > 1:
        hours = int(sys.argv[1])
    if len(sys.argv) > 2:
        top_n = int(sys.argv[2])
    
    result = main(hours=hours, top_n=top_n)
    exit(0 if result["success"] else 1)

