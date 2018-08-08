# xonsh_shells
Various xonsh modules/scripts to make life more interesting.

## CIDR

Simple little tool for deriving network address information from CIDR
ranges.

```python
from CIDR import CIDR
def _cidr(args):
    arg = args[0]
    if isinstance(arg, int) or arg.isnumeric():
        c = CIDR('0.0.0.0/0')
        return c.convert(int(arg))
    return CIDR(arg)
aliases['cidr'] = _cidr
```

## shared_cache

Provides an alias that can be used to share environment variables between
xonsh instances.

```python
# put something like this in your .xonshrc
share PATH

# Now if you change $PATH in one shell, it'll be changed in every shell
(after a hitting return there).
```

## aws_role

This one is very useful if you have multiple AWS roles (and maybe multiple
chef servers).  The below command will switch you to use either an existing
AWS session token for the named AWS profile, or get you a new one (possibly
asking for an MFA token code).  While you're at it, the `knife` command
will use the knife-$PROFILE.rb file (much as if you'd done a `knife block
$PROFILE`.

```python
import aws_role
aws_role default arn:aws:iam::xxxxxxxxxx:role/Shiny-Admin-Role
```
If you provide an invalid role, it'll list the available roles for you.
