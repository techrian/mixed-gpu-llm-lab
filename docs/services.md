# Optional persistent user services

The example units are named **`qwen3.8_flash_next_strata.service`** and **`glm5.3_maya_strata.service`**.
Project Maya is based on Strata, with its engine adapted for GLM-5.3-Flash.
Their `Conflicts=` and ordering directives make a start request stop the other model before starting the selected one.
The examples launch the profile-rendered runtime configuration. Adjust their clone paths first.

```bash
mkdir -p "$HOME/.config/systemd/user"
cp models/qwen3.8-flash-next/systemd/qwen3.8_flash_next_strata.service "$HOME/.config/systemd/user/"
cp models/glm5.3-flash-maya/systemd/glm5.3_maya_strata.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
# Qwen is the selected startup model; GLM remains available manually.
systemctl --user disable glm5.3_maya_strata.service
systemctl --user enable --now qwen3.8_flash_next_strata.service
```

For an earlier installation, stop and disable `strata-qwen.service` and `project-maya-glm.service`,
then archive or remove their unit files before installing the renamed units above.
Historical benchmark captures retain the service names used when they were recorded.

For boot startup before login, the account needs lingering enabled (`loginctl show-user "$USER" -p Linger`).
An administrator can enable it with `loginctl enable-linger USERNAME`. This is separate from `systemctl --user enable`.

## Manual control

```bash
systemctl --user start qwen3.8_flash_next_strata.service
systemctl --user stop qwen3.8_flash_next_strata.service
systemctl --user restart qwen3.8_flash_next_strata.service

systemctl --user start glm5.3_maya_strata.service
systemctl --user stop glm5.3_maya_strata.service
systemctl --user restart glm5.3_maya_strata.service

systemctl --user status qwen3.8_flash_next_strata.service glm5.3_maya_strata.service
journalctl --user -u qwen3.8_flash_next_strata.service -f
journalctl --user -u glm5.3_maya_strata.service -f
```

Choose one enabled startup unit. Starting GLM manually does not change which model is enabled for the next boot.
Both units block process swap with `MemorySwapMax=0`. They do not disable host swap globally.
Resolve any older services using the same GPUs or port before adopting these examples.
