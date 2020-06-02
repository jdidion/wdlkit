{% for decl in declarations %}{{ format_type(decl.type) }} {{decl.name}}{% if decl.expr %} = {{ format_expression(decl.expr) }}{% endif %}
{% endfor %}