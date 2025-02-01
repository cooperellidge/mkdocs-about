DEFAULT_TEMPLATE = """{% if header -%}
{{ header }}
{% else -%}
Projects by this author.
{% endif -%}

{% if related_projects -%}
## Related Projects
{% for repo in related_projects -%}
- [{{ repo.name }}]({{ repo.url }}): {{ repo.description }}
{% endfor -%}

{% endif -%}
{% if other_projects -%}
## Other Projects
{% for repo in other_projects -%}
- [{{ repo.name }}]({{ repo.url }}): {{ repo.description }}
{% endfor -%}
{% endif -%}"""
