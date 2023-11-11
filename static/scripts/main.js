$(function() {

    var socket = io();

    socket.on('receiving_photo', function(data) { // получаем с сервера ответы по сокету для rtsp
        data = JSON.parse(data);
        console.log(data);
        $("form").after(`
            <div class="flex_blocks img_block" style="margin-top:40px; width: 80%;">
                <img class="imgs_size" src="${data[1]}"/>
            </div>
            <div class="text">время распознавания: ${data[0]}</div>
        `)
    });

    $('#files_input').change(function() {
        var files_name = $('#files_input').val();
        $('#link').prop('disabled', true);
        console.log(files_name);
    });

    $('#link').change(function() {
        $('#files_input').prop('disabled', true);
    }); 

    $("#upload_file").on("submit", function(event) { // подтверждение формы
        var form_data = new FormData(this); // получаем файлики с формы
        var link = form_data.get("link");

        if (link != null) { // Если ссылка RTSP
            $("#send").text("Отправлено");
            socket.emit('link_socket', link);
        }
        else {
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
                                $(".loading_block").css({display: "flex"});
                            }
                        }
                    }, false);
                
                return xhr;
                },
                type: 'POST',
                url: '/upload_video',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: function(data) {
                    $("#send").text("Обработано");
                    $(".loading_block").css({display: "none"});
                    data = JSON.parse(data);
                    console.log(data);
                    let id = data[0];
                    for (let i = 1; i < data.length; i++) {
                        $(".container").append(`
                        <div class="titles middle_title anim_slide">${data[i]["input_filename"]}</div>
                        `);

                        if (data[i]["best_seqs"] != "") {
                            $(".container").append(`
                                <div class="titles little_title anim_slide">Обнаруженнное оружие</div>
                            `);
                        }
                        for (let j = 0; j < data[i]["best_seqs"].length; j++) { // добавляем гарантированные случаи
                            let carousel = data[i]["best_seqs"][j];
                            $(".container").append(`
                            <div class="flex_blocks carusel_block anim_slide">
                                <div class="flex_blocks img_block">
                                    <img class="nav_arrow" src="../static/imgs/arrows.png" style="transform: rotate(180deg);"/>
                                    <img class="imgs_size" src="${carousel[0][1]}" style="margin-left: 20px; margin-right: 20px;"/>
                                    <img class="nav_arrow" src="../static/imgs/arrows.png"/>
                                </div>
                                <div class="flex_blocks information_block">
                                    <div class="flex_blocks text page_num">1/${carousel.length}</div>
                                    <div class="text">время распознавания: ${carousel[0][0]}</div>
                                </div>
                                </div> 
                                <div class="btn_block">
                                    <div class="flex_blocks upload_btn mark_btn">Верно</div>
                                    <div class="flex_blocks upload_btn mark_btn">Ошибка</div>
                                </div> 
                            </div>
                            `)
                            let arrow_left = $(".nav_arrow").eq(-2);
                            let arrow_right = $(".nav_arrow").eq(-1);
                            let main_img = $(".imgs_size:last");
                            let num = $(".page_num:last");
                            let time = $(".text:last");
        
                            let p = 0;
        
                            arrow_right.on("click", function(){
                                console.log(p);
                                if (p < carousel.length - 1) {
                                    p++;
                                    main_img.attr("src", carousel[p][1]);
                                    num.text((p + 1) + "/" + carousel.length);
                                    time.text("время распознавания: " + carousel[p][0])
                                }
                            });
                            arrow_left.on("click", function(){
                                console.log(p);
                                if (p > 0) {
                                    p--;
                                    main_img.attr("src", carousel[p][1]);
                                    num.text((p + 1) + "/" + carousel.length);
                                    time.text("время распознавания: " + carousel[p][0])
                                }
                            });
                        }
        
                        $(".container").append(`
                            <div class="titles little_title anim_slide">Помогите нам улучшить распознавание, отметив неверные случаи </div>
                        `);
        
                        for (let j = 0; j < data[i]["ok_seqs"].length; j++) { // добавляем карусели для не гарантированных случев
                            let carousel = data[i]["ok_seqs"][j];
                            $(".container").append(`
                            <div class="flex_blocks carusel_block anim_slide">
                                <div class="flex_blocks img_block">
                                    <img class="nav_arrow" src="../static/imgs/arrows.png" style="transform: rotate(180deg);"/>
                                    <img class="imgs_size" src="${carousel[0][1]}" style="margin-left: 20px; margin-right: 20px;"/>
                                    <img class="nav_arrow" src="../static/imgs/arrows.png"/>
                                </div>
                                <div class="flex_blocks information_block">
                                    <div class="flex_blocks text page_num">1/${carousel.length}</div>
                                    <div class="text">время распознавания: ${carousel[0][0]}</div>
                                </div> 
                                <div class="btn_block">
                                    <div class="flex_blocks upload_btn mark_btn">Верно</div>
                                    <div class="flex_blocks upload_btn mark_btn">Ошибка</div>
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
        
                            arrow_right.on("click", function(){
                                console.log(p);
                                if (p < carousel.length - 1) {
                                    true_btn.text("Верно");
                                    p++;
                                    main_img.attr("src", carousel[p][1]);
                                    num.text((p + 1) + "/" + carousel.length);
                                    time.text("время распознавания: " + carousel[p][0])
                                }
                            });
                            arrow_left.on("click", function(){
                                console.log(p);
                                if (p > 0) {
                                    false_btn.text("Ошибка");
                                    p--;
                                    main_img.attr("src", carousel[p][1]);
                                    num.text((p + 1) + "/" + carousel.length);
                                    time.text("время распознавания: " + carousel[p][0])
                                }
                            });
        
                            true_btn.on("click", function() {
                                true_btn.text("Спасибо");
                                $.ajax({
                                    xhr: function() {
                                        var xhr = new window.XMLHttpRequest();                            
                                        return xhr;
                                    },
                                    type: 'POST',
                                    url: '/user_feedback',
                                    data: JSON.stringify([carousel[p][1], "1"]),
                                    contentType: false,
                                    cache: false
                                },
                                );
                            });
                            false_btn.on("click", function() {
                                false_btn.text("Спасибо");
                                $.ajax({
                                    xhr: function() {
                                        var xhr = new window.XMLHttpRequest();                            
                                        return xhr;
                                    },
                                    type: 'POST',
                                    url: '/user_feedback',
                                    data: JSON.stringify([carousel[p][1], "0"]),
                                    contentType: false,
                                    cache: false
                                },
                                );
                            });
                        }
                    }
                    $(".container").append(`
                        <a class="flex_blocks upload_btn send_btn anim_slide" style="margin: 80px;">Экспорт в архив</a>
                    `)
                    
                    console.log(id);
                    $(".send_btn:last").on("click", function(e){
                        $(".send_btn:last").text("Идёт архивация...");
                        $.ajax({
                            xhr: function() {
                                var xhr = new window.XMLHttpRequest();                            
                                return xhr;
                            },
                            type: 'POST',
                            url: '/send_archive',
                            data: JSON.stringify(id),
                            contentType: false,
                            cache: false,
                            success: function(data){
                                $(".send_btn:last").text("Скачивание");
                                e.preventDefault();  //stop the browser from following
                                console.log(data);
                                window.location.href = data;
                            }
                        },
                        );
                    });

                    

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
        }
        event.preventDefault();
    });
});