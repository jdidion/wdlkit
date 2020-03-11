task {{ name }} {{ "{" }}{% if inputs %}
{{ inputs | indent(2, True) }}
{% endif %}{% if post_inputs %}
{{ post_inputs  | indent(2, True) }}
{% endif %}{% if command %}
{{ command  | indent(2, True) }}
{% endif %}{% if outputs %}
{{ outputs  | indent(2, True) }}
{% endif %}{% if runtime %}
{{ runtime  | indent(2, True) }}
{% endif %}{% if meta %}
{{ meta  | indent(2, True) }}
{% endif %}{% if parameter_meta %}
{{ parameter_meta  | indent(2, True) }}
{% endif %}}