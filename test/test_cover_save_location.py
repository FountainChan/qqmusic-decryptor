#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_cover_save_location():
    print('='*60)
    print('封面保存位置验证测试')
    print('='*60)
    print()
    
    test_dir = '/g/QQMusic/Decrypted/VipSongsDownload/林峯'
    expected_cover_path = '/g/QQMusic/Decrypted/VipSongsDownload/林峯/A Time 4 You 新曲+精选/cover.jpg'
    
    print(f'测试目录: {test_dir}')
    print(f'期望封面路径: {expected_cover_path}')
    print()
    
    if os.path.exists(expected_cover_path):
        print(f'OK: 封面文件存在: {expected_cover_path}')
        print(f'OK: 文件大小: {os.path.getsize(expected_cover_path)} bytes')
        print()
        
        if 'A Time 4 You 新曲+精选' in expected_cover_path:
            print('OK: 封面在专辑子目录中（正确）')
        elif '林峯' == expected_cover_path.split('/')[-2]:
            print('OK: 封面在歌手目录中（对于直接在歌手目录的专辑是正确的）')
        else:
            print('WARNING: 封面位置未知')
        print()
        
        singer_dir = '/g/QQMusic/Decrypted/VipSongsDownload/林峯/cover.jpg'
        if os.path.exists(singer_dir):
            print(f'ERROR: 封面同时存在于歌手目录: {singer_dir}')
        else:
            print('OK: 封面不在歌手目录中（正确）')
        
        print()
        print('目录结构验证:')
        print('-'*60)
        
        for root, dirs, files in os.walk(test_dir):
            level = root.replace(test_dir, '').count(os.sep)
            indent = '  ' * level
            print(f'{indent}{os.path.basename(root)}/')
            
            for file in files:
                if file == 'cover.jpg':
                    print(f'{indent}  📷 {file} <- 封面文件')
                    if 'A Time 4 You 新曲+精选' in root:
                        print(f'{indent}    OK: 在专辑子目录中（正确）')
                    else:
                        print(f'{indent}    WARNING: 位置未知')
                    print()
        
        print('-'*60)
        print()
        print('验证结果:')
        print(f'OK: 封面保存到: {os.path.dirname(expected_cover_path)}')
        print(f'OK: 封面文件名: {os.path.basename(expected_cover_path)}')
        print(f'OK: 完整路径: {expected_cover_path}')
    else:
        print(f'ERROR: 封面文件不存在: {expected_cover_path}')
        print()
        print('可能的原因:')
        print('1. 封面保存逻辑有问题')
        print('2. 目录结构不匹配')
        print('3. 权限问题')
    
    print()
    print('='*60)
    print('测试完成')
    print('='*60)

if __name__ == '__main__':
    test_cover_save_location()
