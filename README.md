# homeassistant-airstage-integration

This is an integration of the Fujitsu AC Cloud AIRSTAGE into home assistant.

### Installation

Copy this folder to `<config_dir>/custom_components/airstage/`.

Add the following entry in your `configuration.yaml`:

```yaml
light:
  - platform: example_light
    host: HOST_HERE
    username: USERNAME_HERE
    password: PASSWORD_HERE_OR_secrets.yaml
```