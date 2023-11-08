$(function() {
    $('#files_input').change(function() {
        var files_name = $('#files_input').val();
        $('#link').prop('disabled', true);
        console.log(files_name);
    });

    $('#link').change(function() {
        $('#files_input').prop('disabled', true);
    }); 

    $("#upload_file").on("submit", function(event) {
        var form_data = new FormData(this); // получаем файлики с формы
        $.ajax({
            xhr: function() {
                var xhr = new window.XMLHttpRequest();
        
                // обновление прогресс бара
                xhr.upload.addEventListener("progress", function(evt){
                    if (evt.lengthComputable) {
                        var percentComplete = evt.loaded / evt.total;
                        $("#send").text(Math.round(percentComplete * 100) + "%");
                    }
                }, false);
               
               return xhr;
            },
            type: 'POST',
            url: '/uploadajax',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                console.log(data);
                $("#send").text("Загружено");

                var arrow_left = $(".nav_arrow").eq(0);
                var arrow_right = $(".nav_arrow").eq(1);
                var main_img = $(".imgs_size:last");
                var num = $(".text:last");

                main_img.attr("src", data[0][1]);
                var i = 0;

                console.log(arrow_left, arrow_right, num);
                arrow_right.on("click", function(){
                    if (i < data.length - 1) {
                        i++;
                        main_img.attr("src", data[i][1]);
                        num.text((i + 1) + "/" + data.length);
                    }
                });
                arrow_left.on("click", function(){
                    if (i >= data.length - 1) {
                        i--;
                        main_img.attr("src", data[i][1]);
                        num.text((i + 1) + "/" + data.length);
                    }
                });

                /*
                for (var i = 0; i < data.length; i++) {
                    $(".titles").eq(1).after(`
                    <div class="flex_blocks case_block">
                        <div class="flex_blocks img_block">
                            <img class="imgs_size" src="${data[i][1]}"/>
                            <div class="text">время распознавания ${data[i][0]}<br></div>
                        </div>  
                    </div>
                    `);
                    console.log($(".case_block .upload_btn").eq(1));
                    $(".case_block .upload_btn").eq(0).on("click", function() {
                        $.ajax({
                            xhr: function() {
                                var xhr = new window.XMLHttpRequest();                            
                               return xhr;
                            },
                            type: 'POST',
                            url: '/user_feedback',
                            data: "1",
                            contentType: false,
                            cache: false
                        },
                        );
                    });
                    $(".case_block .upload_btn").eq(1).on("click", function() {
                        $.ajax({
                            xhr: function() {
                                var xhr = new window.XMLHttpRequest();                            
                               return xhr;
                            },
                            type: 'POST',
                            url: '/user_feedback',
                            data: "0",
                            contentType: false,
                            cache: false
                        },
                        );
                    });

                    var img = $(".imgs_size").eq(0);
                        console.log(img.prop('naturalWidth'));
                        var widthK = img.prop('naturalWidth') / img.prop("width");
                        var heightK = img.prop('naturalHeight') / img.prop("height");
                        img.on("mousemove", function(e) {
                            let x = e.pageX,
                                y = e.pageY;
                            console.log(`${(x - img.offset().left) * widthK}:${(y - img.offset().top) * heightK}`);
                        });
                };
                */
            },
        });
        event.preventDefault();
    });

});