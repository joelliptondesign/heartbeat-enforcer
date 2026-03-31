"""Main application module."""


def main():
    """Main application entry point."""
    from . import auth, config
    
    print("Starting application...")
    print(f"Configuration: {config.get_settings()}")
    auth.initialize()
    print("Application ready")


if __name__ == "__main__":
    main()
