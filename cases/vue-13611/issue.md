# Slot <template> not working when its name starts with an underscore (_) since v3.5.14

Reported by @laurens94 on 2025-07-10

### Vue version

v3.5.14 - v3.5.17

### Link to minimal reproduction

https://play.vuejs.org/#eNq9Vd9P3DAM/les7gEJHa2mbS+3gsbuhrYJhjSQ9rAiyLW+u0CaVElaOCH+9znN9ReFaUzTpD609mf7s+t8uQ8OiyKsSgymQWwxLwSzeJBIgPgjM3jMNqq09TdZGj9Ue3y5nwRMbmZKZtxyJWdrTG8+o8YfXIi5SgJ4pZnMVG6EspLlPmmdpmhfAQ4NCCVXwAzcIjCNkDYZmRAb0Cgz1JwQds0NuGQTekVArZUGlaalNmG80L2c5+R2QMgUGrljASuUsGYVglWAd9xY4LLOkqq8UBKlDVt2UUMvjgbzANiaz8rFrAnrmmpn88pyK7puyZXxCozdCKSRpUooPYWVRpRJcHBVg6+gjb5V+sbEEYV0qfs8nqh3mZWauYH9ac024AV1vWHUehwNtuQR1dikmhcWBJMr4mENbYVBW/oJc0qkLfRzwlKrHHbCQSG3nTvvexFdyRbfmRq0w9Mq0a/+zZbCPlhdIsHjyHMlZsGEmFLokq/Ca6MknYx7l80NMi+4QH1auFzUzRRqj/PZTYG15WcSVNzinqlWe0Ix2t4kmBDAGaNUcOrIGz7UIVGZs5wnwcWkzcT0CgkzpfdPZ9/wzuEbZ2lwjksu8UjpmWDGHHEUWV3YddLicpWVAp9J4p3f0ShRuk48bFHKjJrr4YzVPK2ZDHJfmzsfUWg0qCsq04WoUqd4wopRFGGVqPArTfSkJTdAcALQ6mTePe4Jjfd8kRa1GlcQfOF/wHaBR5070/z0JAn8Zzdyc8OLY76ot2NMXCk75zQX13IY+eiH2k2cZSrKrO5lW5ey6TTa3Y12Q7fwXY3Gmj1jt26sYzPtsy95kcgHt9e0n8N1H0t3d4zjWgid/tIBHAoySQFtPX30oX1TIwcvONXDY/T4FI+J9tnVUkiktmyeUDCNGfnP3UVAj9PvDJesFNbLPZ1ZW4sIXQxbYa1vht4d42Ka/ik705buHW7XJBJA64+aDr5Gf8O02thcI04jw04j20mNOmkF9p9100n2f+nor//4ZUUFiSb96Tfhu/D12+DhF76Uxyk=

### Steps to reproduce

It seems this issue needs the following conditions to arise:

- Have some templates/slots that start their name with an underscore (_)
- The component that contains the templates/slots (`SubComponent.vue`), is placed in the template of another component (`BaseLayout.vue`) and is a sibling of a conditionally rendered template for a slot of `BaseLayout.vue`.

### What is expected?

[The same behavior as in Vue `v3.5.13`](https://play.vuejs.org/#eNq9Vd9P3DAM/les7gEJQSuG9nIraOxuaJtgSANpDyuCXOu7C6RJlaSFE+J/n9Ncf1GYxjRN6kNrf7Y/u86Xh+CoKMKqxGASxBbzQjCLh4kEiD8ygydsrUpbf5Ol8UO1yxcHScDkeqpkxi1XcrrC9PYzavzBhZipJIA3mslM5UYoK1nuk9ZpivYV4MiAUHIJzMAdAtMIaZORCbEGjTJDzQlhV9yAS7ZDrwiotdKg0rTUJoznupfzgtwOCJlCI7csYIUSVqxCsArwnhsLXNZZUpUXSqK0YcsuaujF0WAeABvzeTmfNmFdU+1s3rjSez06ccYrMHYtkEaWKqH0BJYaUSbB4XUNvoY2+k7pWxNHFNKl7vN4pt6Vy/H2Twt69CsqesOo6Tga7McTkrFJNS8sCCaXRMIa2geDtvSz5ZRIW+jnhIVWOWyFg0JuL7fe9yK6ki2+MzVoh6clop/8m/2EA7C6RILHkedKzIIdYkqhC74Mb4ySdCYeXDY3xbzgAvVZ4XJRNxOoPc5n1wXWlp9JUHGLu6Za7grFaG+TYIcAzhilglNH3vChDonKnOU8CS532kxML5EwE3r/dP4N7x2+cZYGZ7jgEo+VngpmzDFHkdWFXSctLldZKfCFJN75HY0SpevEw+alzKi5Hs5YzdOaySD3jbn3EYVGg7qiMl2IKnWKp6wYRRFWiQq/0kRPW3IDBCcArU7m3eOe0HjPF2lRq3EFwef+B2wWeNS5M83OTpPAf3YjN7e8OOHzejvGxJWyM05zcS2HkY9+rN3EWaaizOpeNnUpm06j7e1oO3QL39VorNkLduvGOjbTPvuSl4l8dHtN+zlc97Fod8c4riXQKS8dwKEUkw7Q1tNHH9o3NXLwilM9PEZPT/GYaJ9dLYJEasPmGfnSmJH/wl0B9DjlznDBSmG90NOZtbWI0JWwkdT6TujdLi6m6Z+yM23pxuF2RSIBtP6o6eBr9HdLq43NBeI0Muw0sp3UqBOvrv+slY1Y/5de/vpfX1VUkLSE/vF++C7c2w8efwHe18Ck): the template is being rendered for `_slot2`

### What is actually happening?

The default slot content is being rendered and not replaced with the template content.

### Any additional comments?

Since Vue `v3.5.14` this issue occurs. As a workaround I locked the version to `v3.5.13`.
