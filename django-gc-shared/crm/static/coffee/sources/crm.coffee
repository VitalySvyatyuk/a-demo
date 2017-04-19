getCookie = (name) ->
  cookieValue = null
  if document.cookie and document.cookie isnt ""
    cookies = document.cookie.split(";")
    i = 0

    while i < cookies.length
      cookie = jQuery.trim(cookies[i])

      # Does this cookie string begin with the name we want?
      if cookie.substring(0, name.length + 1) is (name + "=")
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      i++
  return cookieValue

addJob = (job_function, args) ->
  jobsCount += 1
  $("#no-operations-left").hide()
  $("#operations-pending").show()
  $("#operation-status").addClass("operation-status-inprogress")
  $("#operations-count").html(jobsCount)
  job_function(args...)

addNewCall = (crm_id, comment) ->
  $.ajax(
    type: "POST"
    data:
      crm_id: crm_id
      comment: comment
      csrfmiddlewaretoken: getCookie("csrftoken")

    dataType: "json"
    url: "/ajax/save/call"
    error: () ->
      jobFinished()
      alert("Произошла ошибка! Информация о звонке не была сохранена.")

    success: (data) ->
      jobFinished()
      call_tag = "<span title=#{data["call"][2]}>#{data["call"][1]}</span>"
      crm_row = $("#crm-#{crm_id}")
      $(".latest-call", crm_row).html(call_tag)
      call_count = $(".call-count", crm_row)
      call_count.html(parseInt(call_count.html()) + 1)
  )

addNewLinkRequest = (crm_id, account_id, comment) ->
  $.ajax(
    type: "POST"
    data:
      crm_id: crm_id
      account_id: account_id
      comment: comment
      csrfmiddlewaretoken: getCookie("csrftoken")

    dataType: "json"
    url: "/ajax/save/link_request"
    error: () ->
      jobFinished()
      alert("Произошла ошибка! Заявка на закрепление не была сохранена.")

    success: (data) ->
      jobFinished()
      $("#link-request-span-acc-" + account_id).prepend("<img src=\"/static/img/icon_ok.png\" title=\"Вы только что создали заявку.\" />")
  )

editPlannedCall = (crm_id, new_date) ->
  $.ajax(
    type: "POST"
    data:
      crm_id: crm_id
      new_date: new_date
      csrfmiddlewaretoken: getCookie("csrftoken")

    dataType: "json"
    url: "/ajax/save/planned_call"
    error: () ->
      jobFinished()
      alert("Произошла ошибка! Информация о дате следующего звонка не была сохранена.")

    success: (data) ->
      jobFinished()
      crm_row = $("#crm-" + crm_id)
      $(".planned-call span", crm_row).html(new_date)
  )

saveComment = (crm_id, comment) ->
  $.ajax(
    type: "POST"
    data:
      crm_id: crm_id
      comment: comment
      csrfmiddlewaretoken: getCookie("csrftoken")

    dataType: "json"
    url: "/ajax/save/comment"
    error: () ->
      jobFinished()
      alert("Произошла ошибка! Комментарий не был сохранён.")

    success: (data) ->
      jobFinished()
  )

saveNewCustomer = (crm_id, comment, status, next_call_date=false) ->
  $.ajax(
    type: "POST"
    data:
      crm_id: crm_id
      comment: comment
      next_call_date: next_call_date
      status: status
      csrfmiddlewaretoken: getCookie("csrftoken")

    dataType: "json"
    url: "/ajax/save/new_customer_result"
    error: () ->
      jobFinished()
      alert("Произошла ошибка! Звонок новому клиенту не был сохранён.")

    success: (data) ->
      jobFinished()
  )

jobFinished = () ->
  jobsCount -= 1
  if jobsCount is 0
    $("#no-operations-left").show()
    $("#operations-pending").hide()
    $("#operation-status").removeClass("operation-status-inprogress")
  $("#operations-count").html(jobsCount)

showAccountData = (crm_id) ->
  addJob(loadAccountData, [crm_id])

loadAccountData = (crm_id) ->
  $.ajax
    type: "POST"
    data:
      crm_id: crm_id
      csrfmiddlewaretoken: getCookie("csrftoken")

    dataType: "html"
    url: "/ajax/load/account_data"
    error: ->
      jobFinished()
      alert "Не удалось получить данные о пользователе"

    success: (data) ->
      jobFinished()
      $("#crm-" + crm_id + " .account-data").html(data)

showCallHistory = (crm_id) ->
  $("#callinfo-dialog").html("<img src=\"/static/img/ajax-loader.gif\" alt=\"...\"/>")
  $("#callinfo-dialog").dialog("open")
  addJob(loadCallHistory, [crm_id])

getNewCustomer = (customer_type) ->
  $("#new-customer-data").html("<img src=\"/static/img/ajax-loader.gif\" alt=\"...\"/>")
  $("#get-new-customer-dialog").dialog("open")
  addJob(getNewCustomerData, [customer_type])

getNewCustomerData = (customer_type) ->
  $.ajax
    type: "POST"
    data:
      csrfmiddlewaretoken: getCookie("csrftoken")
      customer_type: customer_type

    dataType: "html"
    url: "/ajax/load/new_customer_data"
    error: (jqXHR) ->
      jobFinished()
      if jqXHR.status == 404
        if customer_type == "demo"
          alert "Новых демо-пользователей нет. Попробуйте пустого."
        else if customer_type == "real"
          alert "Новых реальных пользователей нет. Попробуйте демо."
        else if customer_type == "empty"
          alert "Новых пустых пользователей нет."
        else if customer_type == "ib"
          alert "Новых пользователей с IB-счетами нет."
        else if customer_type == "failed_call"
          alert "Нет пользователей, кому не удалось дозвониться в предыдущие дни."
      else
        alert "Ошибка: не удалось получить данные о пользователе."

    success: (data) ->
      jobFinished()
      $("#new-customer-data").html(data)

loadCallHistory = (crm_id) ->
  $.ajax
    type: "POST"
    data:
      crm_id: crm_id
      csrfmiddlewaretoken: getCookie("csrftoken")

    dataType: "json"
    url: "/ajax/load/call"
    error: () ->
      jobFinished()
      alert "Невозможно загрузить информацию о звонках"

    success: (data) ->
      jobFinished()
      call_table = "<table class='call-history-table'><thead><tr><th>Дата</th><th>Комментарий</th><th>Звонил(а)</th></tr></thead><tbody>"
      for cid of data["calls"]
        c = data["calls"][cid]
        call_table += "<tr><td>#{c["date"]}</td><td>#{c["comment"]}</td><td>#{c["caller"]}</td></tr>"
      call_table += "</tbody></table>"
      $("#callinfo-dialog").html(call_table)

window.addNewLinkRequestDialog = (crm_id, account_id, mt4_id) ->
  $("#link-req-crm-id").val(crm_id)
  $("#link-req-mt4acc-django-id").val(account_id)
  $("#link-req-tip-mt4-id").html(mt4_id)
  $("#link-req-comment").autocomplete(
    source: ["Закрепить за ",
      "Есть контакт. Закрепить за ",
      "Пошаговое сопровождение на всех этапах. Закрепить за ",
      "Депонирование после контакта с менеджером. Заменить ____ на ",
      "Ошибка при предыдущем креплении. Заменить ____ на ",
      "Есть контакт. Заменить ___ на "]
    delay: 100
    minLength: 0
  ).focus ->
    $(this).autocomplete("search", "") if @value is ""

  $("#add-link-request-dialog").dialog("open")

jobsCount = 0
oldComment = ""

$(() ->
  $("#add-call-dialog").dialog(
    autoOpen: false
    height: 300
    width: 350
    modal: true
    buttons:
      "Создать звонок": () ->
        addJob addNewCall, [$("#crm-id").val(), $("#call-comment").val()]
        $(this).dialog("close")

      "Отмена": () ->
        $(this).dialog("close")

    close: () ->
      $("#call-comment").val("")
      $("#crm-id").val("")
  )

  $("#add-link-request-dialog").dialog(
    autoOpen: false
    height: 250
    width: 400
    modal: true
    buttons:
      "Создать заявку": () ->
        addJob(addNewLinkRequest, [$("#link-req-crm-id").val(), $("#link-req-mt4acc-django-id").val(), $("#link-req-comment").val()])
        $(this).dialog("close")

      "Отмена": () ->
        $(this).dialog("close")

    close: () ->
      $("#link-req-crm-id").val("")
      $("#link-req-mt4acc-django-id").val("")
      $("#link-req-comment").val("")
  )

  $("#plannedcall-change-dialog").dialog(
    autoOpen: false
    height: 300
    width: 350
    modal: true
    buttons:
      "Ок": () ->
        addJob(editPlannedCall, [$("#plannedcall-crm-id").val(), $("#plannedcall-date").val()])
        $(this).dialog("close")

      "Отмена": () ->
        $(this).dialog("close")

    close: () ->
      $("#plannedcall-date").val("")
      $("#plannedcall-crm-id").val("")
  )

  $(".add-call").click(() ->
    crm_id = $(this).parent().parent().parent().attr("id").match(/\d+/)[0]
    $("#crm-id").val(crm_id)
    $("#add-call-dialog").dialog("open")
    return false
  )

  $(".latest-call").click(() ->
    crm_id = $(this).parent().parent().parent().attr("id").match(/\d+/)[0]
    showCallHistory(crm_id)
    return false
  )

  $(".account-data a").click(() ->
    crm_id = $(this).parent().parent().parent().attr("id").match(/\d+/)[0]
    showAccountData(crm_id)
    return false
  )

  $("#get-new-customer-button").click(() ->
    getNewCustomer(customer_type="real")
  )

  $("#get-new-demo-customer-button").click(() ->
    getNewCustomer(customer_type="demo")
  )

  $("#get-new-empty-customer-button").click(() ->
    getNewCustomer(customer_type="empty")
  )

  $("#get-new-ib-customer-button").click(() ->
    getNewCustomer(customer_type="ib")
  )

  $("#get-failed-call-customer-button").click(() ->
    getNewCustomer(customer_type="failed_call")
  )

  $(".planned-call img").click(() ->
    crm_id = $(this).parent().parent().parent().attr("id").match(/\d+/)[0]
    $("#plannedcall-crm-id").val(crm_id)
    $("#plannedcall-change-dialog").dialog("open")
  )

  $("#callinfo-dialog").dialog(
    autoOpen: false
    height: "auto"
    width: 500
  )

  $("#get-new-customer-dialog").dialog(
    autoOpen: false
    height: 550
    width: 550
    modal: true
    buttons:
      "Подтвердить звонок": () ->
        addJob(saveNewCustomer, [$("#new-customer-crm-pk").val(), $("#new-customer-call-comment").val(), "success", $("#plannedcall-date-new-customer").val()])
        $(this).dialog("close")

      "Не удалось связаться": () ->
        addJob(saveNewCustomer, [$("#new-customer-crm-pk").val(), $("#new-customer-call-comment").val(), "failure"])
        $(this).dialog("close")

      "Клиент рег. офиса": () ->
        addJob(saveNewCustomer, [$("#new-customer-crm-pk").val(), $("#new-customer-call-comment").val(), "regional_office"])
        $(this).dialog("close")

      "Отмена": () ->
        $(this).dialog("close")

    close: () ->
      $("#new-customer-call-comment").val("")
  )

  $(".comment-column").click(() ->
    span = $(".comment-text", this)
    unless span.hasClass("textarea-active")
      span.wrapInner("<textarea>")
      span.addClass("textarea-active")
      $("textarea", this).focus()
      oldComment = $("textarea", this).val()
      $("textarea", this).blur(() ->
        $(this).parent().removeClass("textarea-active")
        comment_value = $(this).val()
        crm_id = $(this).parent().parent().parent().attr("id").match(/\d+/)[0]
        $(this).parent().text(comment_value)
        unless comment_value is oldComment
          addJob(saveComment, [crm_id, comment_value])
      )
  )


  $("#agent_code_filter").submit(() ->
    window.location = "/by_agent_code/0".replace("0", $("#agent_code_input").val().toString())
    false
  )
)

