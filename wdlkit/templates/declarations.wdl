{% for decl in declarations %}{{ decl.type }} {{decl.name}}{% if decl.expr %} = {{ format_expression(decl.expr) }}{% endif %}
{% endfor %}