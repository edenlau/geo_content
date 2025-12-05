import { cn } from '../../utils/cn';

interface RTLWrapperProps {
  children: React.ReactNode;
  languageCode: string;
  writingDirection: 'ltr' | 'rtl';
  className?: string;
}

export function RTLWrapper({
  children,
  languageCode,
  writingDirection,
  className,
}: RTLWrapperProps) {
  const isRTL = writingDirection === 'rtl';
  const isArabic = languageCode.startsWith('ar-');
  const isChinese = languageCode.startsWith('zh-');

  return (
    <div
      dir={writingDirection}
      lang={languageCode}
      className={cn(
        'prose prose-gray max-w-none',
        isRTL && 'rtl-content',
        isArabic && 'font-arabic',
        isChinese && 'font-chinese',
        className
      )}
    >
      {children}
    </div>
  );
}

export default RTLWrapper;
