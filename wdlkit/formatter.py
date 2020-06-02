from enum import Enum
import json
from pathlib import Path
import re
import textwrap
from typing import Any, Dict, Optional, Sequence, Tuple, cast

from jinja2 import Environment, PackageLoader, Template
from WDL import (
    Call,
    Conditional,
    Decl,
    Document,
    Env,
    Expr,
    Scatter,
    StructTypeDef,
    Task,
    Type,
    Workflow,
    WorkflowNode,
    WorkflowSection,
)
from WDL.Tree import DocImport

from wdlkit.ast import WorkflowBodyGraph


SourceDoc = Tuple[str, Path]
"""Represents a WDL source document - a tuple of (URL, local path)"""


class WdlTemplate(Enum):
    """
    Enumeration of Jinja2 templates that are used to render a WDL document.
    """

    CALL = "call"
    COMMAND = "command"
    CONDITIONAL = "conditional"
    DECLARATIONS = "declarations"
    DOCUMENT = "document"
    IMPORTS = "imports"
    INPUTS = "inputs"
    META = "meta"
    OUTPUTS = "outputs"
    PARAMETER_META = "parameter_meta"
    RUNTIME = "runtime"
    SCATTER = "scatter"
    STRUCT = "struct"
    TASK = "task"
    WORKFLOW = "workflow"
    WORKFLOW_BODY = "workflow_body"


def _create_jinja2_env():
    env = Environment(loader=PackageLoader("wdlkit"))
    env.filters["dedent"] = textwrap.dedent
    return env


class Formatter:
    """
    WDL document formatter.
    """

    _JINJA2_ENV = _create_jinja2_env()
    _JSON_ENCODER = json.JSONEncoder(indent=2)
    _UNQUOTE_RE = re.compile(r"^(\s+)\"(.+?)\":", re.M)
    _UNQUOTE_REPL = r"\1\2:"

    @staticmethod
    def format_type(ty: Type.Base) -> str:
        """
        Custom type formatting method, mostly to deal with the fact that miniwdl
        __str__ does not put a space after the ',' for Map and Pair types.
        """
        if isinstance(ty, Type.Map):
            map_type = cast(Type.Map, ty)
            key_str = Formatter.format_type(map_type.item_type[0])
            val_str = Formatter.format_type(map_type.item_type[1])
            s = f"Map[{key_str}, {val_str}]"
            return f"{s}?" if ty.optional else s
        elif isinstance(ty, Expr.Pair):
            pair_type = cast(Type.Pair, ty)
            left_str = Formatter.format_type(pair_type.left_type)
            right_str = Formatter.format_type(pair_type.right_type)
            s = f"Map[{left_str}, {right_str}]"
            return f"{s}?" if ty.optional else s
        elif isinstance(ty, Expr.Array):
            array_type = cast(Type.Array, ty)
            s = f"Array[{Formatter.format_type(array_type.item_type)}]"
            return f"{s}?" if ty.optional else s
        else:
            return str(ty)

    @staticmethod
    def format_expression(expr: Expr.Base) -> str:
        """Simple expression formatter. This should eventually be replaced by one
        that handles wrapping and indenting.

        Args:
            expr: the expression to format

        Returns:
            The formatted expression
        """
        return str(expr)

    @classmethod
    def _get_template(cls, tmpl: WdlTemplate) -> Template:
        return Formatter._JINJA2_ENV.get_template(f"{tmpl.value}.wdl")

    @classmethod
    def _render_template(cls, tmpl: WdlTemplate, **kwargs) -> str:
        return cls._get_template(tmpl).render(
            **kwargs,
            format_expression=Formatter.format_expression,
            format_type=Formatter.format_type
        )

    @classmethod
    def _format_jsonlike(cls, value: Dict[str, Any]) -> Dict[str, str]:
        # format as JSON and unquote hash keys
        return dict(
            (
                key,
                Formatter._UNQUOTE_RE.subn(
                    Formatter._UNQUOTE_REPL, Formatter._JSON_ENCODER.encode(val)
                )[0],
            )
            for key, val in value.items()
        )

    @classmethod
    def format_document(
        cls, doc: Document, contents: Optional[Dict[SourceDoc, str]] = None
    ) -> Dict[str, str]:
        """
        Formats a WDL document and all its imports.

        Args:
            doc: The WDL AST.
            contents: Used to pass the mapping of URI to formatted contents to
                recursive calls on imports. Callers should not need to use this.

        Returns:
            Mapping of URI to formatted document.
        """
        if contents is None:
            contents = {}

        source_doc: SourceDoc = (doc.pos.uri, doc.pos.abspath)

        contents[source_doc] = cls._render_template(
            WdlTemplate.DOCUMENT,
            imports=cls.format_imports(doc.imports),
            structs=[cls.format_struct(s) for s in doc.struct_typedefs or ()],
            workflow=cls.format_workflow(doc.workflow) if doc.workflow else None,
            tasks=[cls.format_task(task) for task in (doc.tasks or ())],
        )

        if doc.imports:
            for imp in doc.imports:
                cls.format_document(imp.doc, contents)

        return contents

    @classmethod
    def format_workflow(cls, value: Workflow) -> str:
        return cls._render_template(
            WdlTemplate.WORKFLOW,
            name=value.name,
            inputs=cls.format_input(value.inputs or ()),
            body=cls.format_workflow_body(value.body),
            outputs=cls.format_output(value.outputs or ()),
            meta=cls.format_meta(value.meta),
            parameter_meta=cls.format_parameter_meta(value.parameter_meta),
        )

    @classmethod
    def format_workflow_body(cls, value: Sequence[WorkflowNode]) -> str:
        graph = WorkflowBodyGraph(*value)
        decls = []
        body = []

        for node in graph.dependency_order():
            if isinstance(node, Decl):
                decls.append(node)
                continue

            if decls:
                body.append(cls.format_declarations(decls))
                decls = []

            if isinstance(node, Call):
                body.append(cls.format_call(node))
            elif isinstance(node, WorkflowSection):
                body.append(cls.format_section(cast(WorkflowSection, node)))

        if decls:
            body.append(cls.format_declarations(decls))

        return cls._render_template(WdlTemplate.WORKFLOW_BODY, body=body)

    @classmethod
    def format_task(cls, value: Task) -> str:
        return cls._render_template(
            WdlTemplate.TASK,
            name=value.name,
            inputs=cls.format_input(value.inputs or ()),
            post_inputs=cls.format_declarations(value.postinputs),
            command=cls.format_command(value.command),
            outputs=cls.format_output(value.outputs),
            runtime=cls.format_runtime(value.runtime),
            meta=cls.format_meta(value.meta),
            parameter_meta=cls.format_parameter_meta(value.parameter_meta),
        )

    @classmethod
    def format_imports(cls, imports: DocImport) -> str:
        return cls._render_template(WdlTemplate.IMPORTS, imports=imports)

    @classmethod
    def format_struct(cls, struct: Env.Binding[StructTypeDef]) -> str:
        return cls._render_template(WdlTemplate.STRUCT, struct=struct.value)

    @classmethod
    def format_input(cls, inputs: Sequence[Decl]) -> str:
        return cls._render_template(WdlTemplate.INPUTS, inputs=inputs)

    @classmethod
    def format_output(cls, outputs: Sequence[Decl]) -> str:
        return cls._render_template(WdlTemplate.OUTPUTS, outputs=outputs)

    @classmethod
    def format_declarations(cls, decls: Sequence[Decl]) -> str:
        return cls._render_template(WdlTemplate.DECLARATIONS, declarations=decls)

    @classmethod
    def format_meta(cls, meta: Dict[str, Any]) -> str:
        return cls._render_template(WdlTemplate.META, meta=cls._format_jsonlike(meta))

    @classmethod
    def format_parameter_meta(cls, parameter_meta: Dict[str, Any]) -> str:
        return cls._render_template(
            WdlTemplate.PARAMETER_META,
            parameter_meta=cls._format_jsonlike(parameter_meta)
        )

    @classmethod
    def format_call(cls, call: Call) -> str:
        return cls._render_template(WdlTemplate.CALL, call=call)

    @classmethod
    def format_section(cls, section: WorkflowSection) -> str:
        subgraph_content = cls.format_workflow_body(section.body)

        if isinstance(section, Conditional):
            return cls.format_conditional(section, body=subgraph_content)
        elif isinstance(section, Scatter):
            return cls.format_scatter(section, body=subgraph_content)

    @classmethod
    def format_conditional(cls, conditional: Conditional, body: str) -> str:
        return cls._render_template(
            WdlTemplate.CONDITIONAL, conditional=conditional, body=body
        )

    @classmethod
    def format_scatter(cls, scatter: Scatter, body: str) -> str:
        return cls._render_template(WdlTemplate.SCATTER, conditional=scatter, body=body)

    @classmethod
    def format_command(cls, command: Expr.String) -> str:
        return cls._render_template(WdlTemplate.COMMAND, command=command)

    @classmethod
    def format_runtime(cls, runtime: Dict[str, Expr.Base]) -> str:
        return cls._render_template(WdlTemplate.RUNTIME, runtime=runtime)
