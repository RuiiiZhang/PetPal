'use client';

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import type { Locale, ToastMessage } from './types';

const translations: Record<Locale, Record<string, string>> = {
  zh: {
    'common.appName': 'PetPal',
    'common.slogan': '让宠物活起来，桌面更精彩',
    'common.startNow': '开始制作',
    'common.loading': '加载中...',
    'common.confirm': '确认',
    'common.cancel': '取消',
    'common.next': '下一步',
    'common.prev': '上一步',
    'common.back': '返回',
    'common.save': '保存',
    'common.error': '出错了',
    'common.retry': '重试',
    'common.success': '成功',
    'common.language': '语言',
    'common.step': '步骤',

    'header.progress': '制作进度',
    'footer.copyright': '© 2025 PetPal. All rights reserved.',
    'footer.privacy': '隐私政策',
    'footer.terms': '服务条款',
    'footer.contact': '联系我们',

    'step.upload': '上传照片',
    'step.style': '选择风格',
    'step.preview': '角色预览',
    'step.animation': '动画预览',
    'step.payment': '支付',
    'step.download': '下载',

    'home.hero.title': '把你的宠物，变成桌面上的陪伴',
    'home.hero.subtitle': '上传一张照片，AI 为你生成精致的桌宠程序与动态贴纸包。每一帧，都是你和它的独特记忆。',
    'home.hero.cta': '开始制作',
    'home.feature1.title': '智能识别',
    'home.feature1.desc': '自动识别宠物品种与特征，精准捕捉每一个独特细节',
    'home.feature2.title': '甄选风格',
    'home.feature2.desc': '三种精心设计的艺术风格，找到最契合你审美的表达',
    'home.feature3.title': '桌面陪伴',
    'home.feature3.desc': '生成可独立运行的桌宠程序，让它在屏幕上自由漫步',
    'home.feature4.title': '动态贴纸',
    'home.feature4.desc': '附赠精美动态贴纸包，让日常对话多一份温度',
    'home.how.title': '制作流程',
    'home.how.step1': '上传照片',
    'home.how.step1.desc': '选择一张或多张清晰的宠物照片',
    'home.how.step2': '选择风格',
    'home.how.step2.desc': '从三种艺术风格中选择最喜爱的',
    'home.how.step3': '确认效果',
    'home.how.step3.desc': '预览并调整，直到满意为止',
    'home.how.step4': '下载桌宠',
    'home.how.step4.desc': '获取桌宠程序与动态贴纸包',
    'home.testimonial.title': '用户心声',
    'home.testimonial1': '"每天看着桌面上走来的小猫，工作的疲惫都被治愈了。"',
    'home.testimonial1.author': '— 小鱼',
    'home.testimonial2': '"贴纸包的质感超出预期，朋友们都想知道在哪做的。"',
    'home.testimonial2.author': '— 阿杰',

    'upload.title': '上传宠物照片',
    'upload.subtitle': '清晰的正面照片能获得更好的效果',
    'upload.dragDrop': '拖放照片至此处，或点击选择',
    'upload.support': '支持 JPG / PNG，单张不超过 10MB',
    'upload.multiHint': '支持多张上传，不同角度效果更佳',
    'upload.petName': '为你的宠物命名',
    'upload.petNamePlaceholder': '例如：小橘、豆豆、Mochi...',
    'upload.breedDetected': '检测到品种',
    'upload.nextBtn': '下一步 · 选择风格',
    'upload.preview': '预览',
    'upload.remove': '移除',
    'upload.atLeastOne': '请至少上传一张照片',
    'upload.enterName': '请输入宠物名字',
    'upload.photosCount': '已选择 {count} 张照片',

    'style.title': '选择风格',
    'style.subtitle': '为你的桌宠甄选一种独特的视觉语言',
    'style.cute.name': '萌趣',
    'style.cute.desc': '柔和圆润的线条，温暖治愈的目光',
    'style.realistic.name': '写实',
    'style.realistic.desc': '还原真实毛发质感，每一根都清晰可见',
    'style.cartoon.name': '插画',
    'style.cartoon.desc': '扁平化设计语言，简约而不简单',
    'style.popular': '最受欢迎',
    'style.price': '¥',
    'style.nextBtn': '下一步 · 生成角色',
    'style.selected': '已选择',

    'preview.title': '角色预览',
    'preview.subtitle': '你的桌宠角色已生成',
    'preview.generating': '正在绘制你的桌宠角色...',
    'preview.satisfied': '满意，继续',
    'preview.redo': '重新生成',
    'preview.adjust': '微调细节',
    'preview.confirming': '确认中...',
    'preview.processing': 'AI 正在精心绘制，请稍候...',

    'animation.title': '动画预览',
    'animation.subtitle': '你的桌宠已经活了起来',
    'animation.generating': '正在制作动画...',
    'animation.satisfied': '满意，去支付',
    'animation.redo': '重新生成',
    'animation.adjust': '微调动作',
    'animation.confirming': '确认中...',
    'animation.processing': '正在赋予角色生命力...',

    'payment.title': '确认支付',
    'payment.subtitle': '完成支付后即可下载全部文件',
    'payment.orderNo': '订单号',
    'payment.petName': '宠物名',
    'payment.selectedStyle': '风格',
    'payment.amount': '支付金额',
    'payment.wechat': '微信支付',
    'payment.alipay': '支付宝',
    'payment.payBtn': '确认支付',
    'payment.processing': '支付处理中...',
    'payment.success': '支付成功！',
    'payment.fail': '支付失败，请重试',

    'download.title': '下载',
    'download.subtitle': '你的桌宠已准备就绪',
    'download.desktopPet': '桌宠程序',
    'download.stickerPack': '动态贴纸包',
    'download.userGuide': '使用说明',
    'download.guide.step1': '下载并解压文件',
    'download.guide.step2': '运行 PetPal.exe（Windows）或 PetPal.app（Mac）',
    'download.guide.step3': '桌宠会出现在屏幕右下角',
    'download.guide.step4': '右键桌宠可切换动作 / 隐藏 / 退出',
    'download.guide.step5': '贴纸包已保存在解压目录中',
    'download.downloadAll': '下载全部文件',
    'download.thanks': '感谢使用 PetPal，愿它为你带来每一天的好心情',
    'download.restart': '再做一只',

    'toast.uploadSuccess': '上传成功',
    'toast.confirmSuccess': '确认成功',
    'toast.paymentSuccess': '支付成功，正在跳转...',
    'toast.error': '操作失败，请重试',
    'toast.networkError': '网络连接异常，请检查后重试',
  },
  en: {
    'common.appName': 'PetPal',
    'common.slogan': 'Bring your pet to life on your desktop',
    'common.startNow': 'Get Started',
    'common.loading': 'Loading...',
    'common.confirm': 'Confirm',
    'common.cancel': 'Cancel',
    'common.next': 'Next',
    'common.prev': 'Previous',
    'common.back': 'Back',
    'common.save': 'Save',
    'common.error': 'Something went wrong',
    'common.retry': 'Retry',
    'common.success': 'Success',
    'common.language': 'Language',
    'common.step': 'Step',

    'header.progress': 'Progress',
    'footer.copyright': '© 2025 PetPal. All rights reserved.',
    'footer.privacy': 'Privacy',
    'footer.terms': 'Terms',
    'footer.contact': 'Contact',

    'step.upload': 'Upload',
    'step.style': 'Style',
    'step.preview': 'Preview',
    'step.animation': 'Animation',
    'step.payment': 'Payment',
    'step.download': 'Download',

    'home.hero.title': 'Turn Your Pet Into a Desktop Companion',
    'home.hero.subtitle': 'Upload a photo, let AI craft an exquisite desktop pet program and animated sticker pack. Every frame, a unique memory of you and your companion.',
    'home.hero.cta': 'Start Creating',
    'home.feature1.title': 'Smart Recognition',
    'home.feature1.desc': 'Automatically identifies breed and features, capturing every unique detail',
    'home.feature2.title': 'Curated Styles',
    'home.feature2.desc': 'Three meticulously designed art styles to match your aesthetic',
    'home.feature3.title': 'Desktop Companion',
    'home.feature3.desc': 'A standalone program that lets your pet roam freely on screen',
    'home.feature4.title': 'Animated Stickers',
    'home.feature4.desc': 'Bonus animated sticker pack to add warmth to your daily chats',
    'home.how.title': 'How It Works',
    'home.how.step1': 'Upload Photos',
    'home.how.step1.desc': 'Select one or more clear photos of your pet',
    'home.how.step2': 'Choose Style',
    'home.how.step2.desc': 'Pick your favorite from three art styles',
    'home.how.step3': 'Confirm Design',
    'home.how.step3.desc': 'Preview and adjust until perfect',
    'home.how.step4': 'Download Pet',
    'home.how.step4.desc': 'Get your desktop pet and sticker pack',
    'home.testimonial.title': 'What Users Say',
    'home.testimonial1': '"Watching my little cat walk across the desktop every day heals all the fatigue of work."',
    'home.testimonial1.author': '— Xiaoyu',
    'home.testimonial2': '"The sticker pack quality exceeded expectations. Everyone asks where I got them."',
    'home.testimonial2.author': '— Ajie',

    'upload.title': 'Upload Pet Photos',
    'upload.subtitle': 'Clear front-facing photos produce the best results',
    'upload.dragDrop': 'Drop photos here, or click to select',
    'upload.support': 'Supports JPG / PNG, max 10MB per file',
    'upload.multiHint': 'Multiple photos welcome — different angles yield better results',
    'upload.petName': 'Name your companion',
    'upload.petNamePlaceholder': 'e.g. Mochi, Biscuit, Whiskers...',
    'upload.breedDetected': 'Breed Detected',
    'upload.nextBtn': 'Next · Choose Style',
    'upload.preview': 'Preview',
    'upload.remove': 'Remove',
    'upload.atLeastOne': 'Please upload at least one photo',
    'upload.enterName': 'Please enter your pet\'s name',
    'upload.photosCount': '{count} photos selected',

    'style.title': 'Choose a Style',
    'style.subtitle': 'Select a unique visual language for your desktop pet',
    'style.cute.name': 'Adorable',
    'style.cute.desc': 'Soft, rounded lines with a warm, healing gaze',
    'style.realistic.name': 'Realistic',
    'style.realistic.desc': 'True-to-life fur texture, every strand visible',
    'style.cartoon.name': 'Illustration',
    'style.cartoon.desc': 'Flat design language, minimal yet expressive',
    'style.popular': 'Most Popular',
    'style.price': '¥',
    'style.nextBtn': 'Next · Generate Character',
    'style.selected': 'Selected',

    'preview.title': 'Character Preview',
    'preview.subtitle': 'Your desktop pet character has been created',
    'preview.generating': 'Crafting your pet character...',
    'preview.satisfied': 'Looks great, continue',
    'preview.redo': 'Regenerate',
    'preview.adjust': 'Fine Tune',
    'preview.confirming': 'Confirming...',
    'preview.processing': 'AI is carefully crafting your pet, please wait...',

    'animation.title': 'Animation Preview',
    'animation.subtitle': 'Your pet is coming alive',
    'animation.generating': 'Creating animation...',
    'animation.satisfied': 'Love it, proceed to payment',
    'animation.redo': 'Regenerate',
    'animation.adjust': 'Adjust Motion',
    'animation.confirming': 'Confirming...',
    'animation.processing': 'Breathing life into your companion...',

    'payment.title': 'Confirm Payment',
    'payment.subtitle': 'Complete payment to download all files',
    'payment.orderNo': 'Order No.',
    'payment.petName': 'Pet Name',
    'payment.selectedStyle': 'Style',
    'payment.amount': 'Amount',
    'payment.wechat': 'WeChat Pay',
    'payment.alipay': 'Alipay',
    'payment.payBtn': 'Confirm Payment',
    'payment.processing': 'Processing payment...',
    'payment.success': 'Payment successful!',
    'payment.fail': 'Payment failed, please retry',

    'download.title': 'Download',
    'download.subtitle': 'Your desktop pet is ready',
    'download.desktopPet': 'Desktop Pet Program',
    'download.stickerPack': 'Animated Sticker Pack',
    'download.userGuide': 'User Guide',
    'download.guide.step1': 'Download and extract the files',
    'download.guide.step2': 'Run PetPal.exe (Windows) or PetPal.app (Mac)',
    'download.guide.step3': 'Your pet will appear in the bottom-right corner',
    'download.guide.step4': 'Right-click the pet to switch actions / hide / exit',
    'download.guide.step5': 'Sticker pack is saved in the extracted folder',
    'download.downloadAll': 'Download All Files',
    'download.thanks': 'Thank you for using PetPal. May it brighten every day',
    'download.restart': 'Make Another',

    'toast.uploadSuccess': 'Upload successful',
    'toast.confirmSuccess': 'Confirmed successfully',
    'toast.paymentSuccess': 'Payment successful, redirecting...',
    'toast.error': 'Operation failed, please retry',
    'toast.networkError': 'Network error, please check connection and retry',
  },
};

interface I18nContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
}

const I18nContext = createContext<I18nContextType>({
  locale: 'zh',
  setLocale: () => {},
  t: (key: string) => key,
});

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>('zh');

  const t = useCallback(
    (key: string, params?: Record<string, string | number>): string => {
      let text = translations[locale][key] || key;
      if (params) {
        Object.entries(params).forEach(([k, v]) => {
          text = text.replace(`{${k}}`, String(v));
        });
      }
      return text;
    },
    [locale]
  );

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within I18nProvider');
  }
  return context;
}

export { translations };
