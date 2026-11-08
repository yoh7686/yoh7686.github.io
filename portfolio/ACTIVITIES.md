# 活動記録の更新

原簿と公開用Markdownは別のファイルです。Driveの原簿を作業用にダウンロードし、公開リポジトリの外に置きます。入力JSONにも原簿と同じ扱いをしてください。

## 原簿のみを更新

入力JSONには id、date（YYYY-MM-DD）、title、kind、status を入れます。status は「予定」「実施未確認」「実施済み」「中止」のいずれかです。公開してよいことを確認した場合は approved: true、演題を記録する場合は subject を指定します。既存の活動を訂正するときは同じIDを指定します。

    node portfolio/update-activity.mjs record /path/to/private.md /path/to/input.json

差分を確認し、Driveの元ファイルを内容だけ差し替えます。

## 実施済みの活動を公開

    node portfolio/update-activity.mjs project /path/to/private.md portfolio/content/activities.md event-example
    python3 portfolio/build.py
    python3 portfolio/check.py

project は指定したIDについて「実施済み」「掲載可」、日本時間の当日以前の実施日を検査し、公開用の項目だけを転記します。演題も公開する場合は --include-subject、Newsにも載せる場合は --news を付けます。既存の公開済み演題は保持します。元ファイルや入力JSONは公開先に含めません。生成後に差分を確認してから公開します。
