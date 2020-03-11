import json
import re
import textwrap
from typing import Any, Callable, Dict, List, Optional, Sequence, cast

from jinja2 import Environment, PackageLoader, Template
from WDL import (
    Call, Conditional, Decl, Document, Env, Expr, Scatter, StructTypeDef, Task,
    Workflow, WorkflowNode, WorkflowSection
)

from wdlkit.ast import WorkflowBodyGraph, WorkflowBodyGraphNode


_JINJA_ENV = Environment(loader=PackageLoader("wdlkit"))
_JINJA_ENV.filters["dedent"] = textwrap.dedent
_TEMPLATE_DOCUMENT = "document.wdl"
_TEMPLATE_WORKFLOW = "workflow.wdl.frag"
_TEMPLATE_TASK = "task.wdl.frag"
_UNQUOTE_RE = re.compile(r"^(\s+)\"(.+?)\":", re.M)
_UNQUOTE_REPL = r"\1\2:"


def _get_template(name: str) -> Template:
    return _JINJA_ENV.get_template(name)


def _frag_renderer(func: Callable, call_wrapped: bool = False):
    is_classmethod = isinstance(func, classmethod)

    if is_classmethod:
        func = cast(classmethod, func).__func__

    prefix = func.__name__[7:]

    def renderer(cls, *args, **kwargs) -> str:
        template_name = f"{prefix}.wdl.frag"
        if args:
            kwargs["value"] = args[0]
        if call_wrapped:
            kwargs = func(cls, **kwargs)
        return _get_template(template_name).render(**kwargs)

    return classmethod(renderer) if is_classmethod else renderer


def _proxy_frag_renderer(func: Callable):
    return _frag_renderer(func, True)


class Formatter:
    @classmethod
    def format_document(
        cls,
        uri: str,
        doc: Document,
        contents: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        if contents is None:
            contents = {}

        contents[uri] = _get_template(_TEMPLATE_DOCUMENT).render(
            structs=[cls.format_struct(s) for s in doc.struct_typedefs or ()],
            workflow=cls.format_workflow(doc.workflow) if doc.workflow else None,
            tasks=[cls.format_task(task) for task in (doc.tasks or ())]
        )

        if doc.imports:
            for imp in doc.imports:
                cls.format_document(imp.uri, imp.doc, contents)

        return contents

    @classmethod
    def format_workflow(cls, workflow: Workflow) -> str:
        return _get_template(_TEMPLATE_WORKFLOW).render(
            name=workflow.name,
            inputs=cls.format_input(workflow.inputs or ()),
            body=cls.format_workflow_body(workflow.body),
            outputs=cls.format_output(workflow.outputs or ()),
            meta=cls.format_meta(workflow.meta),
            parameter_meta=cls.format_parameter_meta(workflow.parameter_meta),
        )

    @classmethod
    def format_task(cls, task: Task) -> str:
        return _get_template(_TEMPLATE_TASK).render(
            name=task.name,
            inputs=cls.format_input(task.inputs or ()),
            post_inputs=cls.format_declarations(task.postinputs),
            command=cls.format_command(task.command),
            outputs=cls.format_output(task.outputs),
            runtime=cls.format_runtime(task.runtime),
            meta=cls.format_meta(task.meta),
            parameter_meta=cls.format_parameter_meta(task.parameter_meta),
        )

    @classmethod
    def format_workflow_body(cls, nodes: Sequence[WorkflowNode]) -> str:
        graph = WorkflowBodyGraph(*nodes)
        decls = []

        for node in graph.dependency_order():
            cls.format_workflow_body_node(node, decls)

    @classmethod
    def format_workflow_body_node(
        cls,
        node: WorkflowBodyGraphNode,
        decls: List[Decl],
        indent=2
    ):
        if isinstance(node.node, Decl):
            decls.append(node.node)
            return

        if decls:
            cls.format_declarations(decls, indent=indent)
            decls.clear()

        if isinstance(node.node, Call):
            cls.format_call(node.node, indent=indent)
        elif isinstance(node, WorkflowSection):
            cls.format_section(node, indent=indent)

    @_frag_renderer
    @classmethod
    def format_struct(cls, value: Env.Binding[StructTypeDef]) -> str:
        pass

    @_frag_renderer
    @classmethod
    def format_input(cls, value: Sequence[Decl]) -> str:
        pass

    @_frag_renderer
    @classmethod
    def format_output(cls, value: Sequence[Decl]) -> str:
        pass

    @_frag_renderer
    @classmethod
    def format_declarations(cls, value: Sequence[Decl], indent: int = 2) -> str:
        pass

    @_proxy_frag_renderer
    @classmethod
    def format_meta(cls, value: Dict[str, Any]) -> str:
        return {"value": cls._format_jsonlike(value)}

    @_proxy_frag_renderer
    @classmethod
    def format_parameter_meta(cls, value: Dict[str, Any]) -> str:
        return {"value": cls._format_jsonlike(value)}

    @classmethod
    def _format_jsonlike(cls, value: Dict[str, Any]) -> str:
        # format as JSON and unquote hash keys
        return _UNQUOTE_RE.subn(_UNQUOTE_REPL, json.dumps(value, indent=2))[0]

    @_frag_renderer
    @classmethod
    def format_call(cls, value: Call, indent: int = 2):
        pass

    @classmethod
    def format_section(cls, section: WorkflowBodyGraphNode, indent: int = 2) -> str:
        subgraph_content = cls.format_workflow_body(
            cast(WorkflowSection, section.node).body
        )
        if isinstance(section.node, Conditional):
            cls.format_conditional(
                section.node, body=subgraph_content, indent=indent + 2
            )
        elif isinstance(section.node, Scatter):
            cls.format_scatter(
                section.node, body=subgraph_content, indent=indent + 2
            )

    @_frag_renderer
    @classmethod
    def format_conditional(cls, value: Conditional, body: str, indent: int = 2):
        pass

    @_frag_renderer
    @classmethod
    def format_scatter(cls, value: Scatter, body: str, indent: int = 2):
        pass

    @_frag_renderer
    @classmethod
    def format_command(cls, value: Expr.String, indent: int = 2):
        pass

    @_frag_renderer
    @classmethod
    def format_runtime(cls, value: Dict[str, Expr.Base]) -> str:
        pass
