import React, { useState } from 'react';
import { changePassword } from '../../api/ApiService';
import { hashPassword } from '../../api/security/securityService';

interface UserSettingsProps {
  userId: string;
  username: string;
  token: string;
  role: string;
  site: string;
  email: string;
}

const UserSettings: React.FC<UserSettingsProps> = ({ userId, username, token, role, site, email }) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [passwordChangeSuccess, setPasswordChangeSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleOpenDialog = () => {
    setOldPassword('');
    setNewPassword('');
    setConfirmNewPassword('');
    setErrorMessage('');
    setPasswordChangeSuccess(false);
    setIsDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
  };

  const handleChangePassword = async () => {
    if (newPassword !== confirmNewPassword) {
      setErrorMessage('The new password and confirm password do not match.');
      return;
    }

    try {
      console.log(oldPassword, newPassword);
      const hashedOldPassword = await hashPassword(oldPassword);
      const hashedNewPassword = await hashPassword(newPassword);
      await changePassword(userId, hashedOldPassword, hashedNewPassword);
      console.log(userId, hashedOldPassword, hashedNewPassword);
      //await changePassword(userId, username, token, role, site, await hashPassword(oldPassword), await hashPassword(newPassword));
      setPasswordChangeSuccess(true);
      // Dopo un breve delay, chiudiamo il dialog
      setTimeout(() => {
        setIsDialogOpen(false);
      }, 15000);
    } catch (error: any) {
      // Gestione dell'errore, ad esempio se l'oldPassword non è corretta
      setErrorMessage(error?.message || 'The old password is incorrect.');
    }
  };

  return (
    <main className="p-6">
      <div className="max-w-4xl mx-auto space-y-12">
        {/* Personal Information Section */}
        <section className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-2xl font-semibold mb-6 text-gray-800 border-b pb-2">Personal Information</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="flex items-center">
              <label htmlFor="first-name" className="block text-sm font-medium text-gray-700 mr-4">
                First Name
              </label>
              <input
                type="text"
                id="first-name"
                className="w-fit p-3 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                defaultValue="John"
              />
            </div>

            <div className="flex items-center">
              <label htmlFor="last-name" className="block text-sm font-medium text-gray-700 mr-4">
                Last Name
              </label>
              <input
                type="text"
                id="last-name"
                className="w-fit p-3 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                defaultValue="Doe"
              />
            </div>
          </div>
        </section>

        {/* Account Details Section */}
        <section className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-2xl font-semibold mb-6 text-gray-800 border-b pb-2">Account Details</h2>
          <div className="flex items-center">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mr-4">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              className="w-fit p-3 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              defaultValue={email}
            />
          </div>

          <div className="mt-6 flex space-x-4">
            <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
              Change Email
            </button>
            <button
              className="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300"
              onClick={handleOpenDialog}
            >
              Change Password
            </button>
          </div>
        </section>
      </div>

      {/* Dialog per la modifica della password */}
      {isDialogOpen && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
            <h3 className="text-xl font-semibold mb-4">Change Password</h3>

            <div className="mb-4">
              <label htmlFor="old-password" className="block text-sm font-medium text-gray-700 mb-1">
                Old Password
              </label>
              <input
                type="password"
                id="old-password"
                className="w-full p-2 border-gray-300 rounded-md"
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
              />
            </div>

            <div className="mb-4">
              <label htmlFor="new-password" className="block text-sm font-medium text-gray-700 mb-1">
                New Password
              </label>
              <input
                type="password"
                id="new-password"
                className="w-full p-2 border-gray-300 rounded-md"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
            </div>

            <div className="mb-4">
              <label htmlFor="confirm-new-password" className="block text-sm font-medium text-gray-700 mb-1">
                Confirm New Password
              </label>
              <input
                type="password"
                id="confirm-new-password"
                className="w-full p-2 border-gray-300 rounded-md"
                value={confirmNewPassword}
                onChange={(e) => setConfirmNewPassword(e.target.value)}
              />
            </div>

            {errorMessage && <p className="text-red-500 mb-4 text-sm">{errorMessage}</p>}
            {passwordChangeSuccess && <p className="text-green-500 mb-4 text-sm">Password cambiata con successo!</p>}

            <div className="flex justify-end space-x-4">
              <button
                className="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300"
                onClick={handleCloseDialog}
              >
                Cancel
              </button>
              {!passwordChangeSuccess && (
                <button
                  className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                  onClick={handleChangePassword}
                >
                  Confirm
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
};


/*
<section className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
  <h2 className="text-2xl font-semibold mb-6 text-gray-800 border-b pb-2">Display Settings (Not Yet Implemented)</h2>
  <div className="flex items-center">
    <label htmlFor="font-size" className="block text-sm font-medium text-gray-700 mr-4">
      Font Size
    </label>
    <select
        id="font-size"
        className="w-fit p-3 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        defaultValue="Normal"
    >
      <option value="Small">Small</option>
      <option value="Normal">Normal</option>
      <option value="Large">Large</option>
    </select>
  </div>

  <div className="mt-8 flex items-center">
    <label htmlFor="pronouns" className="block text-sm font-medium text-gray-700 mr-4">
      Pronouns
    </label>
    <input
        type="text"
        id="pronouns"
        className="w-fit p-3 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        defaultValue="Sir/Mr"
    />
  </div>
</section>
*/

export default UserSettings;
