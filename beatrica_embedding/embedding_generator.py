import os
import json
import mimetypes
from gitignore_parser import parse_gitignore

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from langchain_community.vectorstores import Chroma
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_community.embeddings import HuggingFaceEmbeddings


CACHE_PATH_NAME = "beatrica_code_change_processor_cache"
CACHE_FILE_NAME = "beatrica_code_change_processor_cache.txt"
DEFAULT_MODEL = "gpt-3.5-turbo-1106"
DEFAULT_TEMPERATURE = 0


class BeatricaCodeChangeProcessor:
    def __init__(self, commit_changes, language_model, embeddings=HuggingFaceEmbeddings(), model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE, cache_path="", cache_file=""):
        if cache_path == "":
            cache_path = os.path.join(os.getcwd(), CACHE_PATH_NAME)
        if cache_file == "":
            cache_file = CACHE_FILE_NAME
        self.commit_changes = commit_changes
        self.language_model = language_model
        self.model = model
        self.temperature = temperature
        self.embeddings = embeddings
        self.cache_path = cache_path
        self.cache_file = cache_file

    def process_changes(self):
        updates = []
        for commit_hash, commit_data in self.commit_changes:
            changes = commit_data['changes']
            for file_change in changes:
                file_change_str = f"Commit: {commit_hash}\nMessage: {file_change['commit_message']}\nFile: {file_change['file_path']}\nType: {file_change['change_type']}\n"
                if file_change.get('old_file_path'):
                    file_change_str += f"Old File Path: {file_change['old_file_path']}\n"
                old_lines_info = "Old Lines:\n" + "\n".join(
                    [f"{line['line number']}: {line['line content']}" for line in file_change['old_lines']])
                new_lines_info = "New Lines:\n" + "\n".join(
                    [f"{line['line number']}: {line['line content']}" for line in file_change['new_lines']])
                file_change_str = file_change_str + old_lines_info + "\n" + new_lines_info
                updates.append(file_change_str + "\n")
        return updates

    def process_full_project(self, directory, output_file, gitignore_file=None):
        gitignore_path = os.path.join(directory, gitignore_file) if gitignore_file else None

        matcher = None
        if gitignore_path and os.path.exists(gitignore_path):
            matcher = parse_gitignore(gitignore_path)

        with open(output_file, 'w', encoding='utf-8') as txt_file:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    mime_type, _ = mimetypes.guess_type(file_path)

                    if (
                            (mime_type is not None and mime_type.startswith('text'))
                            or file.endswith('.md')
                    ) and (matcher is None or not matcher(file_path)):
                        txt_file.write(f"# {file}:\n")
                        txt_file.write(f"File Path: {file_path}\n")
                        txt_file.write(f"MIME Type: {mime_type}\n")
                        try:
                            with open(file_path, 'r', encoding='utf-8') as content_file:
                                txt_file.write(content_file.read())
                        except UnicodeDecodeError:
                            print(f"UnicodeDecodeError: {file_path}")
                        txt_file.write("\n")
    def write_full_project_to_file(self, output_file='file_info_and_content_listing.txt', gitignore_file='.gitignore'):
        curr_dir = os.getcwd()
        self.process_full_project(curr_dir, output_file, gitignore_file)
        cache_file = os.path.join(self.cache_path, self.cache_file)
        with open(output_file, 'r', encoding='utf-8') as txt_file:
            file_content = txt_file.read()
        with open(cache_file, 'a', encoding='utf-8') as txt_file:
            txt_file.write(file_content)
        os.remove(output_file)


    def write_updates_to_file(self, updates):
        cache_file = os.path.join(self.cache_path, self.cache_file)
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)
        with open(cache_file, 'w') as f:
            for update in updates:
                update_json = json.dumps(update)
                f.write(update_json + '\n')

    def load_data_from_file(self):
        cache_file = os.path.join(self.cache_path, self.cache_file)
        loader = TextLoader(cache_file)
        return loader.load()

    def delete_cache(self):
        cache_directory = os.path.join(os.getcwd(), CACHE_PATH_NAME)
        for file in os.listdir(cache_directory):
            file_path = os.path.join(cache_directory, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
        if os.path.exists(self.cache_path):
            os.rmdir(self.cache_path)

    def split_data_into_chunks(self, data):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        return text_splitter.split_documents(data)

    def prepare_conversational_retrieval_chain(self, document_chunks):
        cache_directory = os.path.join(os.getcwd(), CACHE_PATH_NAME)
        embeddings_cache = LocalFileStore(cache_directory)
        cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
            underlying_embeddings=self.embeddings,
            document_embedding_cache=embeddings_cache
        )

        vector_db = Chroma.from_documents(document_chunks, cached_embeddings)
        document_retriever = vector_db.as_retriever(search_type="mmr", search_kwargs={"k": 8})

        conversation_memory = ConversationSummaryMemory(llm=self.language_model, memory_key="chat_history", return_messages=True)

        return ConversationalRetrievalChain.from_llm(self.language_model, retriever=document_retriever, memory=conversation_memory)

    def process(self):
        updates = self.process_changes()
        self.write_updates_to_file(updates)
        self.write_full_project_to_file()
        data = self.load_data_from_file()
        document_chunks = self.split_data_into_chunks(data)
        return self.prepare_conversational_retrieval_chain(document_chunks)
