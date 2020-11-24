from server.webserver.main import run, __stop

if __name__ == '__main__':
    try:
        run()
    except SystemExit as e:
        print(e)
        __stop()
    except KeyboardInterrupt as e:
        print(e)
        __stop()
    except Exception as e:
        print(e)
        __stop()