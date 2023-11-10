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
        var link = form_data.get("link");
        var files = $("#files_input")[0].files;

        for (var i = 0; i < files.length; i++) { // Если пользователь отправляет архив, то оставляем только его
            var ext = files.item(i).name.split('.').pop().toLowerCase();
            console.log(ext);
            if ((ext == 'zip') || (ext == 'rar') || (ext == '7zip') || (ext == '7z')) {
                console.log("Загружен массив!", files.item(i));
                form_data = new FormData();
                form_data.append('file', files[i]);;
                break;
            }
        }

        $.ajax({
            xhr: function() {
                var xhr = new window.XMLHttpRequest();
        
                // обновление прогресс бара
                xhr.upload.addEventListener("progress", function(evt){
                    if (evt.lengthComputable) {
                        var percentComplete = evt.loaded / evt.total;
                        $("#send").text(Math.round(percentComplete * 100) + "%");
                        if (percentComplete == 1) {
                            $("#send").text("Идёт обработка...");
                        }
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
                $("#send").text("Обработано");
                data = JSON.parse(data);
                console.log(data);
                for (let i = 0; i < data.length; i++) {
                    console.log(data[i]);
                    $(".container").append(`
                    <div class="titles" style="margin-top: 80px; font-size: 40px;">${data[i]["input_filename"]}</div>
                    `);

                    for (let key in data[i]["best_seqs"]) { // добавляем гарантированные случаи
                        $(".container").append(`
                            <div class="flex_blocks img_block">
                                <img class="imgs_size" src="${data[i]["best_seqs"][key]}"/>
                            </div>
                            <div class="text">время распознавания: ${key}</div>
                        `);
                    }
    
                    $(".container").append(`
                        <div class="titles" style="margin-top: 80px; font-size: 40px;">Помогите нам улучшить распознавание</div>
                    `);
    
                    for (let j = 0; j < data[i]["ok_seqs"].length; j++) { // добавляем карусели для не гарантированных случев
                        let carousel = data[i]["ok_seqs"][j];
                        let dates = Object.keys(carousel);
                        console.log(carousel, dates);

                        $(".container").append(`
                        <div class="flex_blocks carusel_block">
                            <div class="flex_blocks img_block">
                                <img class="nav_arrow" src="../static/imgs/arrows.png" style="transform: rotate(180deg);"/>
                                <img class="imgs_size" src="${carousel[dates[0]]}" style="margin-left: 20px; margin-right: 20px;"/>
                                <img class="nav_arrow" src="../static/imgs/arrows.png"/>
                            </div>
                            <div class="flex_blocks information_block">
                                <div class="flex_blocks text page_num">1/${dates.length}</div>
                                <div class="text">время распознавания: ${dates[0]}</div>
                            </div> 
                            <div class="btn_block">
                                <div class="flex_blocks upload_btn">Верно</div>
                                <div class="flex_blocks upload_btn">Ошибка</div>
                            </div> 
                        </div>
                        `)
                        let arrow_left = $(".nav_arrow").eq(-2);
                        let arrow_right = $(".nav_arrow").eq(-1);
                        let main_img = $(".imgs_size:last");
                        let num = $(".page_num:last");
                        let time = $(".text:last");
                        let true_btn = $(".upload_btn").eq(-2);
                        let false_btn = $(".upload_btn").eq(-1);
    
                        let p = 0;
    
                        main_img.attr("src", carousel[dates[p]]);
    
                        arrow_right.on("click", function(){
                            console.log(p);
                            if (p < dates.length - 1) {
                                p++;
                                main_img.attr("src", carousel[dates[p]]);
                                num.text((p + 1) + "/" + dates.length);
                                time.text("время распознавания: " + dates[p])
                            }
                        });
                        arrow_left.on("click", function(){
                            console.log(p);
                            if (p > 0) {
                                p--;
                                main_img.attr("src", carousel[dates[p]]);
                                num.text((p + 1) + "/" + dates.length);
                                time.text("время распознавания: " + dates[p])
                            }
                        });
    
                        true_btn.on("click", function() {
                            $.ajax({
                                xhr: function() {
                                    var xhr = new window.XMLHttpRequest();                            
                                    return xhr;
                                },
                                type: 'POST',
                                url: '/user_feedback',
                                data: JSON.stringify([carousel[dates[p]], "1"]),
                                contentType: false,
                                cache: false
                            },
                            );
                        });
                        false_btn.on("click", function() {
                            $.ajax({
                                xhr: function() {
                                    var xhr = new window.XMLHttpRequest();                            
                                    return xhr;
                                },
                                type: 'POST',
                                url: '/user_feedback',
                                data: JSON.stringify([carousel[dates[p]], "0"]),
                                contentType: false,
                                cache: false
                            },
                            );
                        });
                    }
                }
                

                /*
                    var img = $(".imgs_size").eq(0); // отслеживание курсора на изображении
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