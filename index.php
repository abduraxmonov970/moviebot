<?php
ob_start();
error_reporting(0);
date_Default_timezone_set('Asia/Tashkent');
define('API_KEY',"7865934297:AAFVxMvEjNhmkZBynscPoZAoy-tVvy2tj2w");
$XasanovUz = "825409017";
$admins = file_get_contents("tizim/admins.txt");
$admin = explode("\n", $admins);
array_push($admin,$XasanovUz);
$bot = bot('getme',['bot'])->result->username;

function getAdmin($chat){
$url = "https://api.telegram.org/bot".API_KEY."/getChatAdministrators?chat_id=@".$chat;
$result = file_get_contents($url);
$result = json_decode ($result);
return $result->ok;
}

function bot($method,$datas=[]){
$url = "https://api.telegram.org/bot".API_KEY."/".$method;
$ch = curl_init();
curl_setopt($ch,CURLOPT_URL,$url);
curl_setopt($ch,CURLOPT_RETURNTRANSFER,true);
curl_setopt($ch,CURLOPT_POSTFIELDS,$datas);
$res = curl_exec($ch);
if(curl_error($ch)){
var_dump(curl_error($ch));
}else{
return json_decode($res);
}}

function addstat($id){
    $dir = "users";
    if (!is_dir($dir)) {
        mkdir($dir, 0777, true);
    }
    $file = "$dir/$id.txt";
    $sana = date("d.m.Y");
    if (!file_exists($file)) {
        file_put_contents($file, $sana);
    }
}

function addblock($id){
$stat=file_get_contents("block");
$check=explode("\n",$stat);
if(!in_array($id,$check)){
file_put_contents("block","\n".$id,8);
}
}

$kanallar=file_get_contents("channel.txt");
function joinchat($id) {
    global $bot;
    $buttons = [];

    $kanallar = file_get_contents("channel.txt");
    if ($kanallar) {
        $ex = explode("\n", $kanallar);
        foreach ($ex as $line) {
            if (!$line) continue;
            $first_ex = explode("@", $line);
            $url = $first_ex[1];
            $ism = bot('getChat', ['chat_id' => "@".$url])->result->title;
            $ret = bot("getChatMember", [
                "chat_id" => "@$url",
                "user_id" => $id,
            ]);
            $stat = $ret->result->status;
            if (!in_array($stat, ["creator", "administrator", "member"])) {
                $buttons[] = [['text' => "❌ " . $ism, 'url' => "https://t.me/$url"]];
            }
        }
    }

    $maxfiy_kanallar = file_get_contents("channel2.txt");
    $buttons = [];

    if ($maxfiy_kanallar) {
        $ex = explode("\n", trim($maxfiy_kanallar));
        for ($i = 0; $i < count($ex); $i += 2) {
            if (!isset($ex[$i + 1])) continue;
            $link = trim($ex[$i]);
            $kanalid = trim($ex[$i + 1]);
            $fayl_nomi = "tizim/$kanalid.txt";
            if (!file_exists($fayl_nomi) || !in_array($id, explode("\n", trim(file_get_contents($fayl_nomi))))) {
                $buttons[] = [['text' => "❌ Maxfiy kanal", 'url' => $link]];
            }
        }
    }

    if (!empty($buttons)) {
        $buttons[] = [['text' => "🔄 Tekshirish", 'callback_data' => "checksuv"]];
        bot('sendMessage', [
            'chat_id' => $id,
            'text' => "<b>⚠️ Botdan to'liq foydalanish uchun quyidagi kanallarga obuna bo'ling!</b>",
            'parse_mode' => 'html',
            'disable_web_page_preview' => true,
            'reply_markup' => json_encode(['inline_keyboard' => $buttons]),
        ]);
        return false;
    }
    return true;
}
?>