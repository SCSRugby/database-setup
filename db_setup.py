import dotenv, os, paramiko, subprocess, zipfile, requests



# setup github ssh key for auth
def ssh_auth():
    if not os.path.isfile(HOME + "/.ssh/github"):
        print("Generating rsa ssh keys for github. Please go to https://github.com/settings/keys and enter the public key from github.pub into a new ssh key for access.")
            
        private_key_path = HOME + "/.ssh/github"
        public_key_path = HOME + "/.ssh/github.pub"
        key_type = "rsa"
        key = paramiko.RSAKey.generate(bits=2048)

        with open(private_key_path, "w") as private_key_file:
            key.write_private_key(private_key_file)

        with open(public_key_path, "w") as public_key_file:
            public_key_file.write(f"{key.get_name()} {key.get_base64()}")
        
        print("Once your ssh key is set in github, press ENTER to continue.")
        input()
    else:
        print("You already have ssh keys for github setup.")


# setup git config for auth
def setup_git():    
    try:
        subprocess.run(["git", "config", "--global", "user.name", os.getenv("GIT_NAME")])
        subprocess.run(["git", "config", "--global", "user.email", os.getenv("GIT_EMAIL")])
    except subprocess.CalledProcessError as e:
        print("An error has occoured: ", e)

# clone relevant repos
def git_clone():
    repos = [("git@github.com:matthew-sirman/database-manager.git", "/database-manager"), ("git@github.com:matthew-sirman/encrypt.git", "/encrypt"), ("git@github.com:SCSRugby/pricing-package.git", "/pricing-package")]
    env = {"GIT_SSH_COMMAND":f"ssh -i {HOME}/.ssh/github"}
    try:
        os.makedirs(os.getenv("WHERE_TO_EDIT") + "/Manager")
    except FileExistsError:
        pass
    git_dest = os.getenv("WHERE_TO_EDIT") + "/Manager"
    for repo, dest in repos:
        try:
            subprocess.run(["git", "clone", repo, git_dest + dest], check=True, env=env)
        except subprocess.CalledProcessError as e:
            print("An error has occoured: ", e)





def setup_libraries():
    # # unpack zip with libraries, this is a bit dodgey but hopefully will work/ be easier than doing it by hand
    # # folder with libraries must also contain a folder that contains all the dlls for release and debug of the exe
    print("Unzipping libraries, this may take a while, make sure you have enough disk space!")
    print("Qt is too big to zip so the folder specified in the environment will also recieve " \
          "an executable installer for qt. You will need Qt Creator + debugger support, and under " \
            f"Qt 5.15.0, MSVC 2019 64-bit and QtWebEngine. Use {os.getenv('LIBRARIES_PATH')}/Qt as your installation path.")
    # with zipfile.ZipFile(os.getenv("LIBRARIES_ARCHIVE"), 'r') as zip_ref:
    #     zip_ref.extractall(os.getenv("LIBRARIES_PATH"))

def construct_cmake():
    try:
        f = open(f'{os.getenv("WHERE_TO_EDIT")}/Manager/pricing-package/compile.bat')
        f.write(
            '@echo off\n'\
            'cd /d %~dp0\n'\
            'rmdir /q /s build\n'\
            'mkdir build\n'\
            'mkdir build\\temp\n'\
            'cd build\\temp\n'\
            'cmake ../../\n'\
            'cmake --build . --config Release\n'\
            'cmake --build . --config Debug\n'\
            'move lib ../lib\n'\
            'cd ../\n'\
            'rmdir /s /q temp'
        )
        f.close()
        subprocess.run([f'{os.getenv("WHERE_TO_EDIT")}/Manager/pricing-package/compile.bat'])
    except subprocess.CalledProcessError as e:
        print("An error has occoured: ", e)
    
    cmake = 'cmake_minimum_required(VERSION 3.2)\n'\
    'project(database_manager)\n'\
    'set(CMAKE_CXX_STANDARD 17)\n'\
    'set(CMAKE_CONFIGURATION_TYPES "Debug;Release" CACHE STRING "" FORCE)\n'\
    'if (WIN32)\n'\
    'set(CMAKE_CXX_FLAGS)\n'\
    'else()\n'\
    'set(CMAKE_CXX_FLAGS -pthread)\n'\
    'endif()\n'\
    'find_package(Qt5 REQUIRED COMPONENTS Core Gui Widgets Svg Pdf)\n'\
    f'find_package(Qt5Pdf HINTS "{os.getenv("LIBRARIES_PATH")}/Qt/5.15.0/modules/qtpdf/lib/cmake/Qt5Pdf")\n'\
    f'find_package(Qt5PdfWidgets HINTS "{os.getenv("LIBRARIES_PATH")}/Qt/5.15.0/modules/qtpdf/lib/cmake/Qt5PdfWidgets")\n'\
    f'set(ZLIB_INCLUDE_DIR "{os.getenv("LIBRARIES_PATH")}/zlib/include")\n'\
    f'set(ZLIB_LIBRARY "{os.getenv("LIBRARIES_PATH")}/zlib/zlib.lib")\n'\
    f'set(CURL_INCLUDE_DIRS "{os.getenv("LIBRARIES_PATH")}/curl/include")\n'\
    f'set(CURL_LIBRARY "{os.getenv("LIBRARIES_PATH")}/curl/libcurl.lib")\n'\
    f'set(MY_BUILD_TYPE "Release" CACHE STRING "Choose the type of build (Debug or Release)")\n'\
    f'set(MYSQL_INCLUDE_DIRS "{os.getenv("LIBRARIES_PATH")}/mysql-connector-cpp/include")\n'\
    f'set(MYSQL_LIBRARY "{os.getenv("LIBRARIES_PATH")}/mysql-connector-cpp/lib64/vs14/debug/mysqlcppconn8.lib")\n'\
    f'set(JSON_INCLUDE_DIRS "{os.getenv("LIBRARIES_PATH")}/json/include")\n'\
    f'set(QT_PLUGIN_PATH "{os.getenv("LIBRARIES_PATH")}/Qt/5.15.0/msvc2019_64/plugins")\n'\
    'cmake_path(SET PRICING_INCLUDE_DIR NORMALIZE "${PROJECT_SOURCE_DIR}/../pricing-package/include")\n'\
    'cmake_path(SET PRICING_LIBRAIRY_D NORMALIZE "${PROJECT_SOURCE_DIR}/../pricing-package/build/lib/pricing_package_d.lib")\n'\
    'cmake_path(SET PRICING_LIBRARY NORMALIZE "${PROJECT_SOURCE_DIR}/../pricing-package/build/lib/pricing_package.lib")\n'\
    'include_directories(\n'\
    '   ${CURL_INCLUDE_DIRS}\n'\
    '   ${JSON_INCLUDE_DIRS}\n'\
    '   ${MYSQL_INCLUDE_DIRS}\n'\
    '   ${BOOST_INLUDE_DIRS}\n'\
    '   ${PROJECT_SOURCE_DIR}/ui\n'\
    ')\n'\
    'add_definitions(-DQT_NO_VERSION_TAGGING -DWIN32_LEAN_AND_MEAN -DCURL_STATICLIB -DNOMINMAX)\n'\
    'set(CMAKE_INCLUDE_CURRENT_DIR ON)\n'\
    'set(CMAKE_AUTOUIC ON)\n'\
    'set(CMAKE_AUTOMOC ON)\n'\
    'set(CMAKE_AUTORCC ON)\n'\
    'set(PROJECT_UI ui/MainMenu.ui ui/MainMenu.cpp ui/MainMenu.h)\n'\
    'set(WIDGETS ui/widgets/DynamicComboBox.cpp ui/widgets/DynamicComboBox.h ui/widgets/ActivatorLabel.cpp ui/widgets/ActivatorLabel.h ui/widgets/AddDrawingPageWidget.ui ui/widgets/AddDrawingPageWidget.cpp ui/widgets/AddDrawingPageWidget.h ui/widgets/DrawingViewWidget.ui ui/widgets/DrawingViewWidget.cpp ui/widgets/DrawingViewWidget.h ui/widgets/DrawingView.cpp ui/widgets/DrawingView.h ui/widgets/DimensionLine.cpp ui/widgets/DimensionLine.h ui/widgets/AddLapWidget.cpp ui/widgets/AddLapWidget.h "ui/widgets/addons/ImpactPadGraphicsItem.h" "ui/widgets/addons/ImpactPadGraphicsItem.cpp"  "ui/widgets/addons/BlankSpaceGraphicsItem.h" "ui/widgets/addons/BlankSpaceGraphicsItem.cpp" "ui/widgets/addons/ExtraApertureGraphicsItem.h" "ui/widgets/addons/ExtraApertureGraphicsItem.cpp" "ui/widgets/ExpandingWidget.h" "ui/widgets/ExpandingWidget.cpp" "ui/widgets/Inspector.h" "ui/widgets/Inspector.cpp" "ui/widgets/addons/CentreHoleSetGraphicsItem.h" "ui/widgets/addons/CentreHoleSetGraphicsItem.cpp" "ui/widgets/addons/DeflectorSetGraphicsItem.h" "ui/widgets/addons/DeflectorSetGraphicsItem.cpp" "ui/widgets/addons/DivertorSetGraphicsItem.h" "ui/widgets/addons/DivertorSetGraphicsItem.cpp" "ui/widgets/addons/DamBarGraphicsItem.h" "ui/widgets/addons/DamBarGraphicsItem.cpp")\n'\
    'set(COMPONENT_WINDOWS ui/AddApertureWindow.ui ui/AddApertureWindow.cpp ui/AddApertureWindow.h ui/AddSideIronWindow.ui ui/AddSideIronWindow.cpp ui/AddSideIronWindow.h ui/AddMaterialWindow.ui ui/AddMaterialWindow.cpp ui/AddMaterialWindow.h ui/AddMachineWindow.ui ui/AddMachineWindow.cpp ui/AddMachineWindow.h ui/MaterialPricingWindow.ui ui/MaterialPricingWindow.h ui/MaterialPricingWindow.cpp ui/SideIronPricingWindow.ui ui/SideIronPricingWindow.h ui/SideIronPricingWindow.cpp ui/AddMaterialPriceWindow.ui ui/AddMaterialPriceWindow.h ui/AddMaterialPriceWindow.cpp ui/AddSideIronPriceWindow.ui ui/AddSideIronPriceWindow.h ui/AddSideIronPriceWindow.cpp ui/ExtraPricingWindow.ui ui/ExtraPricingWindow.h ui/ExtraPricingWindow.cpp ui/AddExtraPriceWindow.ui ui/AddExtraPriceWindow.h ui/AddExtraPriceWindow.cpp ui/LabourTimesWindow.h ui/LabourTimesWindow.cpp ui/LabourTimesWindow.ui ui/AddLabourTimesWindow.h ui/AddLabourTimesWindow.cpp ui/AddLabourTimesWindow.ui)\n'\
    'set(QT_RESOURCES res/qtresources.qrc)\n'\
    'add_subdirectory(${PROJECT_SOURCE_DIR}/../encrypt encrypt-build)\n'\
    'add_executable(${PROJECT_NAME} ${EXTRA_ADD_EXECUTABLE_ARGS} ${COMPONENT_WINDOWS} ${WIDGETS} ${PROJECT_UI} ${QT_RESOURCES} main.cpp src/networking/Server.cpp include/networking/Server.h src/networking/Client.cpp include/networking/Client.h guard.h src/networking/NetworkMessage.cpp include/networking/NetworkMessage.h src/networking/TCPSocket.cpp include/networking/TCPSocket.h src/database/DatabaseManager.cpp include/database/DatabaseManager.h src/database/Drawing.cpp include/database/Drawing.h src/database/DatabaseRequestHandler.cpp include/database/DatabaseRequestHandler.h src/database/DatabaseQuery.cpp include/database/DatabaseQuery.h src/database/drawingComponents.cpp include/database/drawingComponents.h include/database/RequestType.h src/database/DatabaseResponseHandler.cpp include/database/DatabaseResponseHandler.h include/database/ComboboxDataSource.h src/database/ComboboxDataSource.cpp include/database/DataSource.h src/database/DrawingSearchResultsModel.cpp include/database/DrawingSearchResultsModel.h packer.h include/database/DrawingPDFWriter.h src/database/DrawingPDFWriter.cpp   "include/database/componentFilters.h" "src/database/componentFilters.cpp" "include/util/format.h" include/util/DataSerialiser.h "ui/widgets/addons/EventTracker.h" "ui/widgets/addons/EventTracker.cpp"  )\n'\
    'include_directories(${PROJECT_NAME} ${PROJECT_SOURCE_DIR}/../encrypt/include ${MYSQL_INCLUDE_DIRS} ${JSON_INCLUDE_DIRS} ${ZLIB_INCLUDE_DIRS} ${PRICING_INCLUDE_DIR})\n'\
    'target_link_libraries(${PROJECT_NAME} encrypt Dnsapi ${MYSQL_LIBRARY} Qt5::Core Qt5::Gui Qt5::Widgets Qt5::Pdf Qt5::PdfWidgets Qt5::Svg ${ZLIB_LIBRARIES})\n'\
    'target_link_libraries(${PROJECT_NAME} debug ${PRICING_LIBRARY_D})\n'\
    'target_link_libraries(${PROJECT_NAME} optimized ${PRICING_LIBRARY})\n'\
    'option(ASAN_ENABLED "Build this target with AddressSanitizer" ON)\n'\
    'if(ASAN_ENABLED)\n'\
    '   if(MSVC)\n'\
    '       target_link_options(${PROJECT_NAME} PUBLIC /NODEFAULTLIB:libcmt.lib)\n'\
    '   else()\n'\
    '    endif()\n'\
    'endif()'

    cmakeFile = open(os.getenv("WHERE_TO_EDIT") + "/Manager/database-manager/CMakeLists.txt", "w")
    cmakeFile.write(cmake)
    

if __name__ == '__main__':
    global HOME
    HOME = os.path.expanduser("~")
    HOME = HOME.replace("\\", "/")
    dotenv.load_dotenv(".env")
    #git_clone()
    construct_cmake()