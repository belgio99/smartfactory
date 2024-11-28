import React from 'react';

const UserSettings: React.FC = () => {
  return (
      <main className="p-6 ">
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
                  defaultValue="john@example.com"
              />
            </div>

            <div className="mt-6 flex space-x-4">
              <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                Change Email
              </button>
              <button className="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300">
                Change Password
              </button>
            </div>
          </section>

          {/* Display Settings Section */}
          <section className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-2xl font-semibold mb-6 text-gray-800 border-b pb-2">Display Settings</h2>
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

        </div>
      </main>
  );
};

export default UserSettings;
