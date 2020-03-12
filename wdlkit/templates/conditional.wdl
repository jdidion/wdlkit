if ({{ conditional.expr }}) {
  {{ body | trim() | indent(2, False) }}
}