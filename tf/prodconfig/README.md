# prodconfig

This directory is a simplified example of the Optiver production config repository.

I'm working of the spec, not the implementation. By that, I mean we have:

```
src
├── us-east-1
│   ├── hosts
│   └── rcon.conf
├── us-west-1
│   ├── hosts
│   └── rcon.conf
└── us-west-2
    ├── app1
    │   ├── app1 -> ../../../bin/caddy
    │   └── app1.xml
    ├── hosts
    └── rcon.conf
bin
└── caddy
    └── 2.9.1
        └── caddy
```

Above, the `us-west-2` is equivalent of a "colo" - I have just used what is already configured by `hashibox` to speed this experiment up.
