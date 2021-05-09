path="$(realpath .)"
echo "[Unit]\nDescription=Muezzin\n\n[Service]\nEnvironment=\"KIVY_AUDIO=sdl2\"\nExecStart=$path/muezzin" > /etc/systemd/system/muezzin.service
systemctl daemon-reload
systemctl start muezzin