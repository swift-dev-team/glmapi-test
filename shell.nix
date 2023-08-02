{pkgs ? import <nixpkgs> {}}:
pkgs.mkShell {
    packages = [
        pkgs.python310
    ];
    shellHook = ''
    source ./.venv/bin/activate
    '';
}
