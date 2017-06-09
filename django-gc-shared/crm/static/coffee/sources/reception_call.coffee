@ReceptionCall = class ReceptionCall
    constructor: () ->
        @switch_to = ko.observable()
        @fio_name = ko.observable()
        @account = ko.observable()
        @show_account = ko.computed(
            () =>
                if not @switch_to()? or @switch_to() in ["free education", "fsfr", "tesla", "other"]
                    return false
                else
                    return true
        )
        @show_description = ko.computed(
            () =>
                if @switch_to()? and @switch_to() == "other"
                    return true
                else
                    return false
        )
        @education = ko.computed(
           () =>
               if @switch_to()?
                   if @switch_to() == "free education"
                       return true
                   else
                       return false
        )
        @can_submit = ko.observable(true)
        @can_get_manager = ko.computed(
            () =>
                if @switch_to()? and @account()?
                    return true
                else
                    return false
        )
        # manager info: values set by set_pm_data method
        @hide_manager_info = ko.computed(
          () =>
            if @switch_to() == "personal manager"
              return false
            else
              return true
        )
        @show_manager_info = ko.observable()
        @pm_name = ko.observable()
        @pm_internal_phone = ko.observable()
        @manager_auto_assigned = ko.observable()
        @show_account_error = ko.observable(false)

    set_pm_data: (pm_name, pm_internal_phone, pm_auto_assigned, error) ->
        if error
            @show_manager_info(false)
            @show_account_error(true)
            return false
        else
            @pm_name(pm_name)
            @pm_internal_phone(pm_internal_phone)
            @manager_auto_assigned(pm_auto_assigned)
            @show_account_error(false)
            @show_manager_info(true)
            return false
