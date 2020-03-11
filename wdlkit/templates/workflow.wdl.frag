workflow {{ name }} {{ "{" }}{% if inputs %}
  {{ inputs }}
{% endif %}{% if body %}
  {{ body }}
{% endif %}{% if outputs %}
  {{ outputs }}
{% endif %}{% if meta %}
  {{ meta }}
{% endif %}{% if parameter_meta %}
  {{ parameter_meta }}
{% endif %}}