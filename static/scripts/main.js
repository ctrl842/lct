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
                for (var i = 0; i < data.length; i++) {
                    $(".titles").eq(1).after(`
                    <div class="flex_blocks case_block">
                        <div class="flex_blocks img_block">
                            <img class="imgs_size" src="${data[i][1]}"/>
                            <div class="text">время распознавания ${data[i][0]}<br></div>
                        </div>
                        <div class="btn_block">
                            <div class="text">Распознавание нейросетью: </div>
                            <div class="flex_blocks upload_btn">Верно</div>
                            <div class="flex_blocks upload_btn">Ошибка</div>
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

                    /*
                    var img = $(".imgs_size").eq(0);
                        console.log(img.prop('naturalWidth'));
                        var widthK = img.prop('naturalWidth') / img.prop("width");
                        var heightK = img.prop('naturalHeight') / img.prop("height");
                        img.on("mousemove", function(e) {
                            let x = e.pageX,
                                y = e.pageY;
                            console.log(`${(x - img.offset().left) * widthK}:${(y - img.offset().top) * heightK}`);
                        });
                    */
                };
            },
        });
        event.preventDefault();
    });
});