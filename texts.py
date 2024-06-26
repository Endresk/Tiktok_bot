from aiogram.utils.markdown import text as g, code, link

text_no_group = g('Сейчас у вас нету ни одной группы в боте\n\n'
                  'Добавив бота в группу, он автоматически уведомит вас, '
                  'о том что он добавлен и предложит следующие действия\\!'
                  )

text_mode_zero = g('Функционал бота позволяет:\n'
                   '1\\. В режиме \\«Бот\\», отправив ссылку на видео Тиктока\n'
                   'вам направится выгруженное видео, с текстом автора или своим\\.\n'
                   '2\\. В режиме «Группа», есть несколько варинтов добавления группы:\n'
                   ' 2\\.1\\. Когда вы добавляете бота в группу, вам необходимо его назначить администратором, '
                   'после добавления, вам придет подтверждение в боте, если он запушен у вас\\.\n'
                   'В этом режиме у администратора/владелеца, есть свойство настройки бота таким образом, '
                   'что им смогут пользоваться и обычные пользователи группы\\. \n'
                   'По-умолчанию это свойство выключено\\.\n'
                   ' 2\\.2\\. После выбора режима «Группа», вам будет представлена инструкция как добавить бота ')

help_tiktok = g('Если вы не вводите текст к видео, то присвоится текст который указал автор в TikTok\n\n'
                'С desktop текст указываете следующим образом\\: \n\\|ссылка на видео из TikTok\\| '
                '\\|двойной перенос строки\\| \\|текст\\|\n\n'
                'Пример:\n',
                code('https://vm.tiktok.com/{num_video}\n\n*Текст*'))