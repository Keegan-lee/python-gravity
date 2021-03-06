import yaml
import os
from gravity import Gravity
from gravity.exceptions import WrongMasterPasswordException
from gravity.instance import set_shared_gravity_instance
from functools import update_wrapper
import click
import logging
log = logging.getLogger(__name__)


def verbose(f):
    """ Add verbose flags and add logging handlers
    """
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        global log
        verbosity = [
            "critical", "error", "warn", "info", "debug"
        ][int(min(ctx.obj.get("verbose", 0), 4))]
        log.setLevel(getattr(logging, verbosity.upper()))
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, verbosity.upper()))
        ch.setFormatter(formatter)
        log.addHandler(ch)

        # GrapheneAPI logging
        if ctx.obj.get("verbose", 0) > 4:
            verbosity = [
                "critical", "error", "warn", "info", "debug"
            ][int(min(ctx.obj.get("verbose", 4) - 4, 4))]
            log = logging.getLogger("grapheneapi")
            log.setLevel(getattr(logging, verbosity.upper()))
            log.addHandler(ch)

        if ctx.obj.get("verbose", 0) > 8:
            verbosity = [
                "critical", "error", "warn", "info", "debug"
            ][int(min(ctx.obj.get("verbose", 8) - 8, 4))]
            log = logging.getLogger("graphenebase")
            log.setLevel(getattr(logging, verbosity.upper()))
            log.addHandler(ch)

        return ctx.invoke(f, *args, **kwargs)
    return update_wrapper(new_func, f)


def offline(f):
    """ This decorator allows you to access ``ctx.gravity`` which is
        an instance of gravity with ``offline=True``.
    """
    @click.pass_context
    @verbose
    def new_func(ctx, *args, **kwargs):
        ctx.obj["offline"] = True
        ctx.gravity = Gravity(**ctx.obj)
        ctx.blockchain = ctx.gravity
        set_shared_gravity_instance(ctx.gravity)
        return ctx.invoke(f, *args, **kwargs)
    return update_wrapper(new_func, f)


def customchain(**kwargsChain):
    """ This decorator allows you to access ``ctx.gravity`` which is
        an instance of gravity. But in contrast to @chain, this is a
        decorator that expects parameters that are directed right to
        ``Gravity)``.

        ... code-block::python

                @main.command()
                @click.option("--worker", default=None)
                @click.pass_context
                @customchain(foo="bar")
                @unlock
                def list(ctx, worker):
                   print(ctx.obj)

    """
    def wrap(f):
        @click.pass_context
        @verbose
        def new_func(ctx, *args, **kwargs):
            newoptions = ctx.obj
            newoptions.update(kwargsChain)
            ctx.gravity = Gravity(**newoptions)
            ctx.blockchain = ctx.gravity
            set_shared_gravity_instance(ctx.gravity)
            return ctx.invoke(f, *args, **kwargs)
        return update_wrapper(new_func, f)
    return wrap


def chain(f):
    """ This decorator allows you to access ``ctx.gravity`` which is
        an instance of gravity.
    """
    @click.pass_context
    @verbose
    def new_func(ctx, *args, **kwargs):
        ctx.gravity = Gravity(**ctx.obj)
        ctx.blockchain = ctx.gravity
        set_shared_gravity_instance(ctx.gravity)
        return ctx.invoke(f, *args, **kwargs)
    return update_wrapper(new_func, f)


def unlock(f):
    """ This decorator will unlock the wallet by either asking for a
        passphrase or taking the environmental variable ``UNLOCK``
    """
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        if not ctx.obj.get("unsigned", False):
            if ctx.gravity.wallet.created():
                while True:
                    if "UNLOCK" in os.environ:
                        pwd = os.environ["UNLOCK"]
                    else:
                        pwd = click.prompt(
                            "Current Wallet Passphrase", hide_input=True)
                    try:
                        ctx.gravity.wallet.unlock(pwd)
                    except WrongMasterPasswordException:
                        click.echo("Incorrect Wallet passphrase!")
                        continue
                    break
            else:
                click.echo("No wallet installed yet. Creating ...")
                pwd = click.prompt(
                    "Wallet Encryption Passphrase",
                    hide_input=True,
                    confirmation_prompt=True)
                ctx.gravity.wallet.create(pwd)
        return ctx.invoke(f, *args, **kwargs)
    return update_wrapper(new_func, f)


def configfile(f):
    """ This decorator will parse a configuration file in YAML format
        and store the dictionary in ``ctx.config``
    """
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        ctx.config = yaml.load(open(ctx.obj["configfile"]))
        return ctx.invoke(f, *args, **kwargs)
    return update_wrapper(new_func, f)


# Aliases
onlineChain = chain
online = chain
offlineChain = offline
unlockWallet = unlock
