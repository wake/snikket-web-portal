import base64
import itertools
import math
import secrets
import typing

from datetime import datetime, timedelta, timezone

import quart.flask_patch  # noqa:F401
from quart import (
    current_app,
    request,
    g,
)

import flask_babel
import flask_wtf
from flask_babel import lazy_gettext as _l
import flask_babel as _

from . import prosodyclient


client = prosodyclient.ProsodyClient()
client.default_login_redirect = "main.login"

babel = flask_babel.Babel()


BYTE_UNIT_SCALE_MAP = [
    "B",
    "kiB",
    "MiB",
    "GiB",
    "TiB",
]


# Mapping from browser language tags to our locale codes
# Browser sends BCP 47 tags (e.g., zh-TW), we use locale codes (e.g., zh_Hant_TW)
LANGUAGE_ALIASES: typing.Dict[str, str] = {
    "zh-TW": "zh_Hant_TW",
    "zh-Hant": "zh_Hant_TW",
    "zh-Hant-TW": "zh_Hant_TW",
    "zh-CN": "zh_Hans_CN",
    "zh-Hans": "zh_Hans_CN",
    "zh-Hans-CN": "zh_Hans_CN",
    "zh": "zh_Hans_CN",  # Default Chinese to Simplified
}


@babel.localeselector  # type:ignore
def selected_locale() -> str:
    g.language_header_accessed = True
    # Check cookie first for user's language preference
    lang_cookie = request.cookies.get('snikket_language')
    if lang_cookie and lang_cookie in current_app.config['LANGUAGES']:
        return lang_cookie

    # Fall back to browser Accept-Language header
    # First, try to match using aliases for Chinese variants
    for lang, quality in request.accept_languages:
        # Normalize the language tag
        normalized = lang.replace("_", "-")
        if normalized in LANGUAGE_ALIASES:
            alias_target = LANGUAGE_ALIASES[normalized]
            if alias_target in current_app.config['LANGUAGES']:
                return alias_target

    # Then try standard best_match
    selected = request.accept_languages.best_match(
        current_app.config['LANGUAGES']
    ) or current_app.config['LANGUAGES'][0]
    return selected


def flatten(a: typing.Iterable, levels: int = 1) -> typing.Iterable:
    for i in range(levels):
        a = itertools.chain(*a)
    return a


def circle_name(c: typing.Any) -> str:
    if c.id_ == "default" and c.name == "default":
        return _l("Main")
    return c.name


# Language names in their native form
LANGUAGE_NAMES: typing.Dict[str, str] = {
    "en": "English",
    "da": "Dansk",
    "de": "Deutsch",
    "fr": "Français",
    "id": "Bahasa Indonesia",
    "it": "Italiano",
    "pl": "Polski",
    "ru": "Русский",
    "sv": "Svenska",
    "uk": "Українська",
    "zh_Hant_TW": "繁體中文",
    "zh_Hans_CN": "简体中文",
}


def language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code, code)


def format_bytes(n: float) -> str:
    try:
        scale = max(math.floor(math.log(n, 1024)), 0)
    except ValueError:
        scale = 0
    try:
        unit = BYTE_UNIT_SCALE_MAP[scale]
        factor = 1024**scale
    except IndexError:
        unit = "TiB"
        factor = 1024**4
    if factor > 1:
        return "{:.1f} {}".format(n / factor, unit)
    return "{} {}".format(n, unit)


def format_last_activity(timestamp: typing.Optional[int]) -> str:
    if timestamp is None:
        return _l("Never")

    last_active = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    # TODO: This 'now' should use the user's local time zone, but we
    # don't have that information. Thus 'today'/'yesterday' may be
    # slightly inaccurate, but compared to alternative solutions it
    # should hopefully be "good enough".
    now = datetime.now(tz=timezone.utc)
    time_ago = now - last_active

    yesterday = now - timedelta(days=1)

    if (
        last_active.year == now.year
        and last_active.month == now.month
        and last_active.day == now.day
    ):
        return _l("Today")
    elif (
        last_active.year == yesterday.year
        and last_active.month == yesterday.month
        and last_active.day == yesterday.day
    ):
        return _l("Yesterday")

    return _.gettext(
        "%(time)s ago",
        time=flask_babel.format_timedelta(time_ago, granularity="day"),
    )


def template_now() -> typing.Dict[str, typing.Any]:
    return dict(now=lambda: datetime.now(timezone.utc))


def add_vary_language_header(resp: quart.Response) -> quart.Response:
    if getattr(g, "language_header_accessed", False):
        resp.vary.add("Accept-Language")
    return resp


def init_templating(app: quart.Quart) -> None:
    app.template_filter("repr")(repr)
    app.template_filter("format_datetime")(flask_babel.format_datetime)
    app.template_filter("format_date")(flask_babel.format_date)
    app.template_filter("format_time")(flask_babel.format_time)
    app.template_filter("format_timedelta")(flask_babel.format_timedelta)
    app.template_filter("format_percent")(flask_babel.format_percent)
    app.template_filter("format_bytes")(format_bytes)
    app.template_filter("flatten")(flatten)
    app.template_filter("circle_name")(circle_name)
    app.template_filter("language_name")(language_name)
    app.template_filter("format_last_activity")(format_last_activity)
    app.context_processor(template_now)
    app.after_request(add_vary_language_header)


def generate_error_id() -> str:
    return base64.b32encode(secrets.token_bytes(8)).decode(
        "ascii"
    ).rstrip("=")


class BaseForm(flask_wtf.FlaskForm):  # type:ignore
    def __init__(self, *args: typing.Any, **kwargs: typing.Any):
        meta = kwargs["meta"] = dict(kwargs.get("meta", {}))
        if "locales" not in meta:
            locale = flask_babel.get_locale()
            if locale:
                meta["locales"] = [str(locale)]

        super().__init__(*args, **kwargs)
