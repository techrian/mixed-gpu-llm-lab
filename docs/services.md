# Optional persistent user services

The example units are named **`strata-qwen.service`** and **`project-maya-glm.service`**.
Their `Conflicts=` and ordering directives make a start request stop the other model before starting the selected one.
The examples launch the profile-rendered runtime configuration. Adjust their clone paths first.

```bash
mkdir -p "$HOME/.config/systemd/user"
cp models/qwen3.8-flash-next/systemd/strata-qwen.service "$HOME/.config/systemd/user/"
cp models/glm5.3-flash-maya/systemd/project-maya-glm.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
# Qwen is the selected startup model; GLM remains available manually.
systemctl --user disable project-maya-glm.service
systemctl --user enable --now strata-qwen.service
```

For boot startup before login, the account needs lingering enabled (`loginctl show-user "$USER" -p Linger`).
An administrator can enable it with `loginctl enable-linger USERNAME`. This is separate from `systemctl --user enable`.

## Manual control

```bash
systemctl --user start strata-qwen.service
systemctl --user stop strata-qwen.service
systemctl --user restart strata-qwen.service

systemctl --user start project-maya-glm.service
systemctl --user stop project-maya-glm.service
systemctl --user restart project-maya-glm.service

systemctl --user status strata-qwen.service project-maya-glm.service
journalctl --user -u strata-qwen.service -f
journalctl --user -u project-maya-glm.service -f
```

Choose one enabled startup unit. Starting GLM manually does not change which model is enabled for the next boot.
Both units block process swap with `MemorySwapMax=0`. They do not disable host swap globally.
Resolve any older services using the same GPUs or port before adopting these examples.
