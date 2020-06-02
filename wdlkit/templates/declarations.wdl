{% for decl in declarations %}{% if loop.index > 1 %}
{% endif %}{{ format_type(decl.type) }} {{decl.name}}{% if decl.expr %} = {{ format_expression(decl.expr) }}{% endif %}{% endfor %}