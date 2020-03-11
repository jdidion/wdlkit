{% for decl in value %}{{ decl.type }} {{decl.name}}{% if decl.expr %} = {{ decl.expr }}{% endif %}
{% endfor %}