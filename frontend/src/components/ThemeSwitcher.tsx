import * as RadioGroup from '@radix-ui/react-radio-group';
import { useSettingsStore } from '../stores/settingsStore';

export function ThemeSwitcher() {
  const { theme, updateSettings } = useSettingsStore();

  const handleThemeChange = (value: string) => {
    updateSettings({ theme: value as any });
    if (value === 'system') {
      document.documentElement.removeAttribute('data-theme');
    } else {
      document.documentElement.setAttribute('data-theme', value);
    }
  };

  return (
    <div className="space-y-3">
      <label className="text-sm font-medium" id="theme-label">Theme</label>
      <RadioGroup.Root 
        className="flex flex-col space-y-2" 
        value={theme} 
        onValueChange={handleThemeChange}
        aria-labelledby="theme-label"
      >
        {[
          { id: 'system', label: 'System default' },
          { id: 'light', label: 'Light' },
          { id: 'dark', label: 'Dark' },
          { id: 'high-contrast', label: 'High contrast' }
        ].map((opt) => (
          <div key={opt.id} className="flex items-center">
            <RadioGroup.Item 
              value={opt.id} 
              id={`theme-${opt.id}`}
              className="bg-white w-5 h-5 rounded-full shadow-[0_2px_10px] shadow-blackA4 hover:bg-violet3 focus:shadow-[0_0_0_2px] focus:shadow-black outline-none cursor-default border border-gray-300 flex items-center justify-center"
            >
              <RadioGroup.Indicator className="flex items-center justify-center w-full h-full relative after:content-[''] after:block after:w-[11px] after:h-[11px] after:rounded-[50%] after:bg-brand" />
            </RadioGroup.Item>
            <label className="text-[15px] leading-none pl-[15px]" htmlFor={`theme-${opt.id}`}>
              {opt.label}
            </label>
          </div>
        ))}
      </RadioGroup.Root>
    </div>
  );
}
