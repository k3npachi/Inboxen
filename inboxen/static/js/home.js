/*!
 * Copyright (c) 2015 Jessica Tallon & Matt Molyneaux
 * Licensed under AGPLv3 (https://github.com/Inboxen/Inboxen/blob/master/LICENSE)
 */

function initForm($form) {
    var inbox = $form.data("inbox-selector");

    $form.submit(function(event) {
        event.preventDefault();
        var description, is_disabled, $this;

        $this = $(this);

        if ($this.data("sending") === "yes") {
            return false;
        }

        $this.find("button").prop("disabled", true);
        $this.find("a.btn").addClass("disabled");
        $this.data("sending", "yes");
        setTimeout(function() {
            $this.data("sending", "no");
            $this.find("button").prop("disabled", false);
            $this.find("a.btn").removeClass("disabled");
        }, 3000);

        description = $this.find("#id_description").val();
        is_disabled = $this.find("#id_disable_inbox").prop("checked");

        $.ajax({
            type: "POST",
            url: $this.attr('action'),
            data: $this.serializeArray(),
            complete: function(xhr, statusText) {
                var $row = $("#" + inbox + " + .row");

                if (xhr.status === 204) {
                    var $inbox_row = $("#" + inbox);
                    var $description_cell = $inbox_row.children(".inbox-description");

                    $description_cell.text(description);

                    if (is_disabled && !$inbox_row.hasClass("inbox-disabled")) {
                        $inbox_row.addClass("inbox-disabled");
                        $inbox_row.find(".inbox-flags").empty();
                        $inbox_row.find(".inbox-flags").append("<div class=\"inline-block__wrapper\"><span class=\"label label-default\" title=\"Inbox has been disabled\">Disabled</span></div>");
                    } else if (!is_disabled && $inbox_row.hasClass("inbox-disabled")) {
                        $inbox_row.removeClass("inbox-disabled");
                        $inbox_row.find(".inbox-flags").empty();
                    }

                    $row.remove();
                } else {
                    var $form = $row.children("div");
                    if (xhr.status === 200) {
                        $form.html(xhr.responseText);
                    } else {
                        $form.html("<div class=\"alert alert-info\">Sorry, something went wrong.</div>");
                        console.log("Form for " + inbox + " failed to POST (" + xhr.status + ")");
                    }
                }
            }
        });
    });
    $("#form-" + inbox + " > a").click(function() {
        var $row = $("#" + inbox + " + .row");
        $row.remove();
    });
}

// adds event listeners for inline forms to be popped in
$(document).ready(function() {
    var $optionButtons = $("#inbox-list .inbox-options a");

    $optionButtons.click(function() {
        var $this = $(this);
        var $row = $this.parents("div.row:has(.inbox-name)");
        var formURL = "/forms/inbox/edit/" + $row.attr("id") + "/";

        if (!$row.next().hasClass("inbox-edit-form-row")) {
            if ($this.data("clicked") === "yes") {
                return false;
            } else {
                $this.data("clicked", "yes");
                $this.addClass("disabled");
                setTimeout(function() {
                    $this.data("clicked", "no");
                    $this.removeClass("disabled");
                }, 3000);
            }

            $.get(formURL, function(data) {
                // double check
                if (!$row.next().hasClass("inbox-edit-form-row")) {
                    $row.after("<div class=\"inbox-edit-form-row row\"><div class=\"col-xs-12\">" + data + "</div></div>");
                    initForm($row.next().find("form"));
                }
            });
        } else if ($row.next().hasClass("inbox-edit-form-row")) {
            $row.next().remove();
        }
        return false;
    });
});
