# Arch X11 Extras

Optional user-level X11/XFCE configs for the Arch Framework 13 setup.

## Included Configs

| Extra | Target | Purpose | Dependencies |
|---|---|---|---|
| `arch-x11/mouse-workspace-buttons.xbindkeysrc` | `~/.xbindkeysrc` | Maps Logitech side buttons to previous/next workspace | `xbindkeys`, `xdotool` |
| `arch-x11/touchpad-workspace-gestures.conf` | `~/.config/libinput-gestures.conf` | Maps three-finger swipes to previous/next workspace | `libinput-gestures`, `xdotool` |
| `arch-x11/lightdm-locale.xprofile` | `~/.xprofile` | Sets `LC_TIME=en_GB.UTF-8` for XFCE/LightDM | generated `en_GB.UTF-8` locale |

## One-Time Setup

Install runtime tools:

```bash
sudo pacman -S xbindkeys xdotool
paru -S libinput-gestures
```

Allow `libinput-gestures` to read touchpad events:

```bash
sudo usermod -aG input $USER
```

Log out or reboot after changing group membership.

Enable touchpad gesture autostart:

```bash
libinput-gestures-setup start autostart
```

Generate the locale used by `xprofile`:

```bash
sudo sed -i 's/#en_GB.UTF-8 UTF-8/en_GB.UTF-8 UTF-8/' /etc/locale.gen
sudo locale-gen
```

## More Detail

See the ArchSetup docs:

- `~/Documents/ArchSetup/extras-peripherals.md`
- `~/Documents/ArchSetup/keybindings-session.md`
- `~/Documents/ArchSetup/arch-framework13-install.md`
