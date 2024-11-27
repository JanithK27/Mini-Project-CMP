function loadloop() {

    setInterval(function() {
        $.ajax({
                data: {
                    name: "Notification"

                },
                type: 'POST',
                url: '/notification'
            })
            .done(function(data) {

                if (data.error) {
                   
                    console.log(data.error)
                } else {
                    if (data.Type == "new_bid") {
                        
                        $('#successAlert').text("New Bid For " + data.Title + ". New BID Price Is Rs " + data.Max_bid + "/=").show();
                        console.log(data.Title, data.Base_Price, data.Max_bid);
                        
                    }

                    if (data.Type == "new_item") {
                        
                        $('#successAlert').text("New Item add. " + data.Title + ". Base price Is Rs " + data.Base_Price + "/=" + " Bid expiry_on" + " " + data.Expiry_Date).show();
                        console.log(data.Title, data.Base_Price, data.Expiry_Date);
                       
                    }
                    $(function() {
                        $("#dialog-message").dialog({
                            modal: true,
                            
                            buttons: {
                                Ok: function() {
                                    $(this).dialog("close");
                                    data.Title = "LOL"
                                    $('#successAlert').hide();

                                    $.ajax({
                                        data: {
                                            name: "Notification_OFF"

                                        },
                                        type: 'POST',
                                        url: '/notification'
                                    })
                                }
                            }
                        });
                      


                    });
                }

            });

    }, 1000);


}

loadloop();