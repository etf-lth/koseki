from os import path, mkdir

import sass  # type: ignore
from flask import Flask


def install_theme(app: Flask, theme_name: str, static_folders: list[str]) -> None:
    folder_theme = path.join(app.root_path, "themes", theme_name)
    folder_scss = path.join(app.root_path, "themes", theme_name, "scss")
    folder_css = path.join(app.root_path, "themes", theme_name, "css")
    file_config = path.join(app.root_path, "themes", theme_name, "theme.cfg")

    # Load theme config
    app.config.from_pyfile(file_config)

    # Optionally load SCSS
    if path.isdir(folder_scss):
        if not path.isdir(folder_css):
            mkdir(folder_css)
        sass.compile(
            dirname=(folder_scss, folder_css),
            output_style="compressed"
        )

    # Install theme into MultiStaticFlask
    # Static folders are prioritized in ascending order, thereby insertion first.
    static_folders.insert(0, folder_theme)
