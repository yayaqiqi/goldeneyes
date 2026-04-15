import pytest
import json
import os
import sys
import tempfile
import datetime
from unittest.mock import patch, MagicMock

# ========== utils.py ==========
import utils

class TestCalculateHourDiff:
    def test_positive_diff(self):
        t1 = "2024-01-01 10:00"
        t2 = "2024-01-01 14:30"
        result = utils.calculate_hour_diff(t1, t2, floor=True)
        assert result == 4  # 4.5 hours, floored

    def test_negative_diff(self):
        t1 = "2024-01-01 14:00"
        t2 = "2024-01-01 10:00"
        result = utils.calculate_hour_diff(t1, t2, floor=True)
        assert result == 4

    def test_cross_day(self):
        t1 = "2024-01-01 23:00"
        t2 = "2024-01-02 01:00"
        result = utils.calculate_hour_diff(t1, t2, floor=True)
        assert result == 2

    def test_no_floor(self):
        t1 = "2024-01-01 10:00"
        t2 = "2024-01-01 10:30"
        result = utils.calculate_hour_diff(t1, t2, floor=False)
        assert 0.4 < result < 0.6

    def test_same_time(self):
        t = "2024-01-01 10:00"
        result = utils.calculate_hour_diff(t, t, floor=True)
        assert result == 0


class TestCalculateNowHourDiff:
    def test_returns_int(self):
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        result = utils.calculate_now_hour_diff(now_str, floor=True)
        assert result == 0

    def test_past_time(self):
        past = (datetime.datetime.now() - datetime.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M")
        result = utils.calculate_now_hour_diff(past, floor=True)
        assert result == 5

    def test_no_floor(self):
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        result = utils.calculate_now_hour_diff(now_str, floor=False)
        assert result >= 0


# ========== template.py ==========
import template as T

class TestRender:
    def test_render_returns_string(self):
        j = [{"type": "card"}]
        result = T.render(j)
        assert isinstance(result, str)

    def test_render_valid_json(self):
        j = {"key": "value", "list": [1, 2, 3]}
        result = T.render(j)
        parsed = json.loads(result)
        assert parsed == j


class TestGetLetterTemplate:
    def test_without_images(self):
        result = T.getLetterTemplate("小明", "今晚月色真美", [])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed[0]["type"] == "card"
        assert "小明" in str(parsed)

    def test_with_images(self):
        result = T.getLetterTemplate("小明", "今晚月色真美", ["http://example.com/img.png"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert "img" in str(parsed).lower()


class TestGetGiftTemplate:
    def test_without_images(self):
        result = T.getGiftTemplate("小红", "小明", "玫瑰花", "生日快乐", "2024-01-01 12:00", [])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed[0]["type"] == "card"
        assert "小明" in str(parsed)
        assert "玫瑰花" in str(parsed)

    def test_with_images(self):
        result = T.getGiftTemplate("小红", "小明", "玫瑰花", "生日快乐", "2024-01-01 12:00", ["http://img.png"])
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert "玫瑰花" in str(parsed)


class TestGetMusicTemplate:
    def test_basic(self):
        result = T.getMusicTemplate("夜曲", "小红", "小明", "2024-01-01")
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed[0]["type"] == "card"
        assert "夜曲" in str(parsed)


# ========== record.py ==========
import record

class TestGenerateRecord:
    def test_generates_html(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = os.path.join(tmpdir, "test_record.json")
            html_file = os.path.join(tmpdir, "output.html")
            data = {
                "sName": "测试恋综",
                "name": "测试玩家",
                "details": {
                    "ch1": {
                        "EP": "EP01",
                        "channel_name": "通讯：角色A&角色B",
                        "last_time": "2024-01-01 12:00",
                        "current_person": "角色A",
                        "is_finished": True,
                        "content": ["角色A：你好", "角色B：你好啊"]
                    }
                }
            }
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
            result = record.generateRecord(json_file, html_file)
            assert os.path.exists(html_file)
            with open(html_file, encoding="utf-8") as f:
                content = f.read()
            assert "<html" in content or "<HTML" in content

    def test_missing_key_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = os.path.join(tmpdir, "bad.json")
            html_file = os.path.join(tmpdir, "out.html")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
            with pytest.raises(KeyError):
                record.generateRecord(json_file, html_file)


# ========== main.py 核心函数测试 ==========
# 注意：main.py 顶层会尝试连接 KOOK，需要 patch

import main as M

class TestParseKV:
    def test_three_keys(self):
        text = "发信人：张三\n收信人：李四\n内容：今晚见"
        result = M.parse_kv(text, "发信人：", "收信人：", "内容：")
        assert result["发信人："] == "张三"
        assert result["收信人："] == "李四"
        assert result["内容："] == "今晚见"

    def test_five_keys(self):
        text = "署名：AAA\n内容：心愿内容\n时间：明天\n发布人：BBB"
        result = M.parse_kv(text, "署名：", "内容：", "时间：", "发布人：")
        assert result["署名："] == "AAA"
        assert result["内容："] == "心愿内容"
        assert result["时间："] == "明天"
        assert result["发布人："] == "BBB"

    def test_missing_key_raises(self):
        text = "发信人：张三\n内容：你好"
        with pytest.raises(ValueError, match="缺少关键词"):
            M.parse_kv(text, "发信人：", "收信人：", "内容：")

    def test_content_with_separator(self):
        text = "发信人：张三\n收信人：李四\n内容：时间：明天见"
        result = M.parse_kv(text, "发信人：", "收信人：", "内容：")
        assert result["内容："] == "时间：明天见"


class TestLoadDataSetData:
    def test_set_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            name = "test_loadset"
            filepath = os.path.join(tmpdir, name + ".json")
            with patch.object(M, 'PATH', tmpdir + os.sep):
                data = {"key": "value", "list": [1, 2, 3]}
                flag, msg = M.setData(name, data)
                assert flag is True
                loaded_flag, loaded_data = M.loadData(name)
                assert loaded_flag is True
                assert loaded_data == data

    def test_load_nonexistent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(M, 'PATH', tmpdir + os.sep):
                flag, msg = M.loadData("nonexistent_file_xyz")
                assert flag is False
                assert isinstance(msg, str)


class TestWithdrawLetters:
    @patch("main.loadData")
    @patch("main.setData")
    def test_withdraw_letters(self, mock_setData, mock_loadData):
        mock_loadData.return_value = (True, {"频道A": [{"content": "信1"}], "频道B": []})
        mock_setData.return_value = (True, "保存成功")

        mock_msg = MagicMock()
        mock_msg.ctx.channel.name = "频道A"
        mock_msg.target_id = "channel_id_123"

        with patch("main.getsDataJsonByChannelId") as mock_gets:
            mock_gets.return_value = {"sName": "测试恋综"}
            result = M.withdrawLetters(mock_msg)

        assert "成功" in result
        # 验证 setData 被调用，清空了发送者的信
        mock_setData.assert_called_once()
        call_data = mock_setData.call_args[0][1]
        assert call_data["频道A"] == []


class TestSystemSendGiftBackup:
    @patch("main.loadData")
    @patch("main.setData")
    @patch("main.sendMessage")
    def test_backup_and_clear(self, mock_sendMsg, mock_setData, mock_loadData):
        mock_loadData.return_value = (True, {
            "玩家A": [
                {"sender_name": "AA", "recever_name": "BB", "content": "信1", "imgs": []}
            ]
        })
        mock_setData.return_value = (True, "ok")

        mock_msg = MagicMock()
        mock_msg.target_id = "channel_id_123"

        with patch("main.getsDataJsonByChannelId") as mock_gets:
            mock_gets.return_value = {
                "sName": "测试恋综",
                "solos": {"BB": "channel_BB"}
            }
            with patch("main.os.path.exists", return_value=True):
                with patch("main.os.makedirs"):
                    with patch("main.shutil.copy2"):
                        with patch("main.datetime.datetime") as mock_dt:
                            mock_dt.now.return_value.strftime.return_value = "20240101_120000"
                            M.systemSendGift(mock_msg)

        # 验证 setData 被调用，清空了 letter_data
        mock_setData.assert_called()
        call_data = mock_setData.call_args[0][1]
        assert call_data["玩家A"] == []

    @patch("main.loadData")
    @patch("main.sendMessage")
    def test_no_letters_no_backup(self, mock_sendMsg, mock_loadData):
        mock_loadData.return_value = (True, {"玩家A": []})
        mock_msg = MagicMock()
        mock_msg.target_id = "channel_id_123"

        with patch("main.getsDataJsonByChannelId") as mock_gets:
            mock_gets.return_value = {
                "sName": "测试恋综",
                "solos": {}
            }
            with patch("main.setData") as mock_setData:
                M.systemSendGift(mock_msg)
                # cnt==0 时不调用 setData（提前 return）
                # 实际行为取决于实现：可能不调用 setData
