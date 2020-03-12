{% for decl in declarations %}{{ decl.type }} {{decl.name}}{% if decl.expr %} = {{ decl.expr }}{% endif %}
{% endfor %}