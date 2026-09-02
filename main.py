from dify_plugin import DifyPluginEnv, Plugin


def main() -> None:
    Plugin(DifyPluginEnv()).run()


if __name__ == "__main__":
    main()
