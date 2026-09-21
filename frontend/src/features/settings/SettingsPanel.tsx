import * as Dialog from '@radix-ui/react-dialog';
import * as Switch from '@radix-ui/react-switch';
import { useTranslation } from 'react-i18next';
import { useSettingsStore } from '../../stores/settingsStore';
import { ThemeSwitcher } from '../../components';

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SettingsPanel({ isOpen, onClose }: SettingsPanelProps) {
  const { t } = useTranslation();
  const settings = useSettingsStore();

  const handleDyslexiaChange = (checked: boolean) => {
    settings.updateSettings({ dyslexiaFont: checked });
    if (checked) {
      document.documentElement.setAttribute('data-dyslexia', 'true');
    } else {
      document.documentElement.removeAttribute('data-dyslexia');
    }
  };

  const handleMotionChange = (checked: boolean) => {
    settings.updateSettings({ reducedMotion: checked });
    if (checked) {
      document.documentElement.setAttribute('data-reduced-motion', 'true');
    } else {
      document.documentElement.removeAttribute('data-reduced-motion');
    }
  };

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-40" />
        <Dialog.Content className="fixed right-0 top-0 bottom-0 w-full max-w-md bg-white shadow-xl z-50 flex flex-col focus:outline-none">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
            <Dialog.Title className="text-lg font-bold text-gray-900 m-0">
              {t('settings.title')}
            </Dialog.Title>
            <Dialog.Close asChild>
              <button className="text-gray-500 hover:text-gray-700 p-1 rounded focus:outline-none focus:ring-2 focus:ring-focus">
                ✕
              </button>
            </Dialog.Close>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-8">
            <ThemeSwitcher />

            <div className="space-y-4">
              <h3 className="font-bold text-sm text-gray-900 uppercase tracking-wider">Accessibility</h3>
              
              <div className="flex items-center justify-between">
                <label htmlFor="dyslexia-switch" className="text-sm font-medium text-gray-700">
                  {t('settings.dyslexia')}
                </label>
                <Switch.Root 
                  id="dyslexia-switch"
                  checked={settings.dyslexiaFont}
                  onCheckedChange={handleDyslexiaChange}
                  className="w-[42px] h-[25px] bg-gray-300 rounded-full relative shadow-[0_2px_10px] shadow-blackA4 focus:shadow-[0_0_0_2px] focus:shadow-black data-[state=checked]:bg-brand outline-none cursor-default"
                >
                  <Switch.Thumb className="block w-[21px] h-[21px] bg-white rounded-full shadow-[0_2px_2px] shadow-blackA4 transition-transform duration-100 translate-x-0.5 will-change-transform data-[state=checked]:translate-x-[19px]" />
                </Switch.Root>
              </div>

              <div className="flex items-center justify-between">
                <label htmlFor="motion-switch" className="text-sm font-medium text-gray-700">
                  {t('settings.reducedMotion')}
                </label>
                <Switch.Root 
                  id="motion-switch"
                  checked={settings.reducedMotion}
                  onCheckedChange={handleMotionChange}
                  className="w-[42px] h-[25px] bg-gray-300 rounded-full relative shadow-[0_2px_10px] shadow-blackA4 focus:shadow-[0_0_0_2px] focus:shadow-black data-[state=checked]:bg-brand outline-none cursor-default"
                >
                  <Switch.Thumb className="block w-[21px] h-[21px] bg-white rounded-full shadow-[0_2px_2px] shadow-blackA4 transition-transform duration-100 translate-x-0.5 will-change-transform data-[state=checked]:translate-x-[19px]" />
                </Switch.Root>
              </div>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
