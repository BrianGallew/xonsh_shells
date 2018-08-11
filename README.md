# xonsh_shells
Various xonsh modules/scripts to make life more interesting.

## CIDR

Simple little tool for deriving network address information from CIDR
ranges.

```xonsh
cidr 10.100.4.0/22
         CIDR range: 10.100.4.0/22
                    Netmask: 255.255.252.0
            Network address: 10.100.4.0
          Broadcast address: 10.100.7.255
         First host address: 10.100.4.1
          Last host address: 10.100.7.254
        Available addresses: 1022
```

## shared_cache

Provides an alias that can be used to share environment variables between
xonsh instances.

```python
xontrib load shared_cache
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
contrib load aws_role
def _role1():
    aws_role default arn:aws:iam::xxxxxxxxxx:role/Read-Only-Role
def _role2():
    aws_role default arn:aws:iam::xxxxxxxxxx:role/Basic-User-Role
def _role3():
    aws_role default arn:aws:iam::xxxxxxxxxx:role/Shiny-Admin-Role
aliases['safe'] = _role1
aliases['read_write'] = _role2
aliases['FEEL_THE_POWER'] = _role3
```
If you provide an invalid role, it'll list the available roles for you.
