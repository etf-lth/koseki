

- Plugins now have a hook system to add html or similar where needed, use something like:
    ```python
    def register_hooks(self, plugin_manager) -> None:
        pass
        # plugin_manager.register_hook("add_form_extra", self._add_form_fields)
        # plugin_manager.register_tab("group__tabs", "access", "Access Control")

    def _add_form_fields(self, form=None, **kwargs) -> str:
         return render_template_string("""
             <h3 class="card-header">Ancillary information</h3>
             <div class="card-body">
                 <div class="row">
                     <div class="col-6 col-md-3">
                         <TODO: figure out how to do the input system validation etc>
                     </div>
                 </div>
             </div>
         """, form=form)
    ```

    - add `{{ render_hooks("add_form_extra", form=form) }}`
    - in tabs used via macros: `{{ group_tabs("", group, get_tabs("group__tabs")) }}`